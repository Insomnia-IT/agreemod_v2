# sync_module.py
import aiohttp
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from grist_updater.config import config as app_config
from typing import Dict, List, Optional
import json
import uuid
from uuid import UUID
import aio_pika
from pathlib import Path
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(module)s] [%(levelname)s]: %(message)s",
    datefmt="%Y.%m.%d %H:%M:%S",
)

# Set RabbitMQ related loggers to WARNING level
logging.getLogger("aio_pika").setLevel(logging.WARNING)
logging.getLogger("aiormq").setLevel(logging.WARNING)
logging.getLogger("connection").setLevel(logging.WARNING)
logging.getLogger("channel").setLevel(logging.WARNING)
logging.getLogger("exchange").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Special constant to indicate record should be skipped
SKIP_RECORD = object()

#TODO: constant for record deletion
DELETE_RECORD = object()
RESTORE_RECORD = object()

class GristSync:
    def __init__(self, state_file='sync_state.json'):
        self.status_mapping: Dict[int, str] = {}  # {grist_status_id: status_code}
        self.roles: List[str] = []
        self.badges_map: Dict[int, str] = {}
        self.roles_mapping: Dict[str, str] = {}
        self.arrival_mapping: Dict[int, str] = {}  # {grist_arrival_type_id: arrival_type_code}
        self.state_file = Path(state_file)
        self.last_sync = self._load_sync_state()
        self.rabbitmq_publisher = None

    def _load_sync_state(self) -> Dict[str, float]:
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки состояния: {e}")
        return {}
    
    def _save_sync_state(self):
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.last_sync, f, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения состояния: {e}")

    @staticmethod
    def get_pg_connection():
        """Подключение к PostgreSQL"""
        return psycopg2.connect(
            dbname=app_config.postgres.name,
            user=app_config.postgres.user,
            password=app_config.postgres.password,
            host=app_config.postgres.host,
            port=app_config.postgres.port
        )

    async def fetch_grist_data(self, table_name: str) -> List[Dict]:
        """Получение данных через SQL API с использованием sql_query"""
        config = next(t for t in TABLES_CONFIG if t['grist_table'] == table_name)
        url = f"{app_config.grist.server}/api/docs/{app_config.grist.doc_id}/sql"
        headers = {"Authorization": f"Bearer {app_config.grist.api_key}"}
        
        base_query = config['sql_query']
        last_sync = self.last_sync.get(table_name)
        
        # Добавляем фильтр по времени, если есть
        where_clause = f"WHERE updated_at >= {last_sync}" if last_sync else ""
        full_query = f"{base_query} {where_clause}"
        print(full_query)
        
        params = {"q": full_query}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"SQL Error ({resp.status}): {error}")
                return await resp.json()

    async def fetch_grist_table(self, table_name: str) -> List[Dict]:
        """Получение данных из таблицы Grist"""
        url = f"{app_config.grist.server}/api/docs/{app_config.grist.doc_id}/tables/{table_name}/records"
        headers = {"Authorization": f"Bearer {app_config.grist.api_key}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    raise Exception(f"Ошибка запроса: {resp.status}")
                data = await resp.json()
                return data.get('records', [])
            
    async def fetch_column_choices(self, table_name: str, column_name: str) -> List[str]:
        """Получение вариантов ролей из метаданных колонки"""
        url = f"{app_config.grist.server}/api/docs/{app_config.grist.doc_id}/tables/{table_name}/columns"
        headers = {"Authorization": f"Bearer {app_config.grist.api_key}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    raise Exception(f"Ошибка: {resp.status}")
                data = await resp.json()
                for col in data.get('columns', []):
                    if col['id'] == column_name:
                        widget_options = json.loads(col['fields'].get('widgetOptions', '{}'))
                        return widget_options.get('choices', [])
                return []
            
    async def _fetch_badges_mapping(self):
        """Получение связи nocode_int_id → badge_id из PostgreSQL"""
        conn = self.get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT nocode_int_id, id FROM badge")
                self.badges_map = {row[0]: row[1] for row in cursor.fetchall()}
        finally:
            conn.close()
            
    async def update_utility_data(self):
        # 2. Получение статусов из таблицы Participations
        participations = await self.fetch_grist_table('Participation_statuses')
        self.status_mapping = {
             p['id']: {
                 "code": p['fields'].get('code'),
                 "name": p['fields'].get('A'),
                 "to_list": p['fields'].get('to_list', True),
                 "comment": p['fields'].get('B')
             }
            for p in participations
        }

        roles = await self.fetch_grist_table('Roles')
        self.roles_mapping = {
            p['id']: {
                "code":p['fields']['Code'],
                "name":p['fields']['Name']}
            for p in roles
        }

        # Fetch arrival types
        arrival_types = await self.fetch_grist_table('Arrival_type')
        self.arrival_mapping = {
            p['id']: {
                "code":p['fields']['code'],
                "name":p['fields']['title']}
            for p in arrival_types
        }
        print(self.arrival_mapping)

        try:
            await self._insert_roles()
        except Exception:
            pass

        try:
            await self._insert_participation_statuses()
        except Exception:
            pass

    async def _insert_roles(self):
        """Вставка ролей в PostgreSQL"""
        conn = self.get_pg_connection()
        try:
            with conn.cursor() as cursor:
                execute_values(
                    cursor,
                    "INSERT INTO participation_role (code, name) VALUES %s",
                    [(role['code'], role['name']) for key, role in self.roles_mapping.items()],
                    template="(%s, %s)"
                )
                conn.commit()
        finally:
            conn.close()

    async def _insert_participation_statuses(self):
        """Вставка статусов участия в PostgreSQL"""
        conn = self.get_pg_connection()
        try:
            with conn.cursor() as cursor:
                for status_id, status in self.status_mapping.items():
                    try:
                        cursor.execute(
                            """
                            INSERT INTO participation_status (code, name, to_list, comment)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (code) DO UPDATE SET
                                name = EXCLUDED.name,
                                to_list = EXCLUDED.to_list,
                                comment = EXCLUDED.comment
                            """,
                            (
                                status.get('code'),
                                status.get('name'),
                                status.get('to_list', True),  # Default to True if not specified
                                status.get('comment')
                            )
                        )
                        conn.commit()
                    except Exception as e:
                        print(f"Error inserting status {status_id}: {e}")
                        conn.rollback()
                        continue
        finally:
            conn.close()

    def order_tables_by_dependencies(self, tables: List[Dict]) -> List[Dict]:
        """Топологическая сортировка таблиц"""
        visited = set()
        ordered = []

        def visit(table):
            if table['grist_table'] not in visited:
                visited.add(table['grist_table'])
                for dep in table.get('dependencies', []):
                    dep_table = next(t for t in tables if t['grist_table'] == dep)
                    visit(dep_table)
                ordered.append(table)

        for table in tables:
            visit(table)
        return ordered

    async def init_rabbitmq(self):
        """Initialize RabbitMQ publisher"""
        if not self.rabbitmq_publisher:
            try:
                rabbitmq_host = os.getenv('RABBITMQ__HOST', 'rabbitmq')
                rabbitmq_user = os.getenv('RABBITMQ__USER', 'guest')
                rabbitmq_password = os.getenv('RABBITMQ__PASSWORD', 'guest')
                rabbitmq_port = os.getenv('RABBITMQ__QUEUE_PORT', '5672')
                rabbitmq_url = f"amqp://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_host}:{rabbitmq_port}/"
                
                self.rabbitmq_publisher = await aio_pika.connect_robust(
                    rabbitmq_url,
                    timeout=30,
                    reconnect_interval=5
                )
                logger.info("Successfully connected to RabbitMQ")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise

    async def close_rabbitmq(self):
        """Close RabbitMQ connection"""
        if self.rabbitmq_publisher:
            await self.rabbitmq_publisher.close()

    async def publish_delete_message(self, table_name: str, record_id: int):
        """Publish delete message to RabbitMQ"""
        if not self.rabbitmq_publisher:
            await self.init_rabbitmq()

        channel = await self.rabbitmq_publisher.channel()
        message = {
            "table_name": table_name,
            "id": record_id
        }
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key="delete_records"
        )
        logger.info(f"Published delete message for record {record_id} in table {table_name}")

    async def sync_table(self, config: Dict):
        """Основной метод синхронизации для одной таблицы"""
        records = await self.fetch_grist_data(config['grist_table'])
        records = records.get('records')
        
        if not records:
            return
        
        context = {
            "status_mapping": self.status_mapping,
            "roles_mapping": self.roles_mapping,
            "badges_map": self.badges_map,
            'arrivals_mapping': self.arrival_mapping,
            "roles": self.roles
        }

        # Преобразование данных
        transformed = []
        for record in records:
            try:
                result = self._transform_record(record, config['field_mapping'], config.get('transformations'), context)
                if result is SKIP_RECORD:
                    continue
                elif result is DELETE_RECORD:
                    # Send delete message to RabbitMQ
                    record_id = self._get_nested_value(record, 'fields.id')
                    await self.publish_delete_message(config['grist_table'], record_id)
                    continue
                transformed.append(result)
            except Exception as e:
                print(f"Error transforming record: {e}")
                continue

        if not transformed:
            return

        # Вставка в PostgreSQL
        conn = self.get_pg_connection()
        try:
            with conn.cursor() as cursor:
                execute_values(
                    cursor,
                    config['insert_query'],
                    transformed,
                    template=config['template']
                )
                conn.commit()
                self.last_sync[config['grist_table']] = datetime.now().timestamp()
        finally:
            conn.close()

        if 'additional_queries' in config:
            conn = self.get_pg_connection()
            try:
                with conn.cursor() as cursor:
                    for query_config in config['additional_queries']:
                        for record in records:
                            # Получаем nocode_int_id бейджа и team_list
                            badge_nocode_id = self._get_nested_value(record, 'fields.id')
                            team_list_raw = self._get_nested_value(record, 'fields.directions_ref') or []

                            if isinstance(team_list_raw, str):
                                # Handle empty string case
                                if not team_list_raw.strip('[]'):
                                    team_list = []
                                else:
                                    team_list = list(map(int, team_list_raw.strip('[]').split(',')))
                            else:
                                team_list = team_list_raw

                            # Преобразуем список в строку формата PostgreSQL ARRAY
                            team_list_str = "{" + ",".join(map(str, team_list)) + "}"
                            print(team_list_str)

                            # Выполняем запрос для текущего бейджа
                            cursor.execute(
                                query_config['insert_query'],
                                (badge_nocode_id, team_list_str, badge_nocode_id)
                            )
                    conn.commit()
            finally:
                conn.close()

    def _transform_record(
        self, 
        record: Dict, 
        mapping: Dict, 
        transformations: Dict,
        context: Dict  # Добавляем контекст
    ) -> tuple:
        """Преобразование структуры записи с контекстом"""
        transformed = []
        for grist_field, pg_field in mapping.items():
            value = self._get_nested_value(record, grist_field)
            
            if transformations and grist_field in transformations:
                # Передаем контекст в функцию преобразования
                value = transformations[grist_field](value, context)
                # If any field transformation returns SKIP_RECORD, skip the entire record
                if value is SKIP_RECORD:
                    return SKIP_RECORD
                elif value is DELETE_RECORD:
                    return DELETE_RECORD
            
            transformed.append(value)
        return tuple(transformed)

    @staticmethod
    def _get_nested_value(data: Dict, path: str):
        """Получение значения из вложенных полей (например: 'fields.updated_at')"""
        keys = path.split('.')
        value = data
        for key in keys:
            value = value.get(key, None)
            if value is None:
                break
        return value

TABLES_CONFIG = [
    {
        'grist_table': 'Teams',
        'insert_query': """
            INSERT INTO direction (
                id, name, type, first_year, last_year, nocode_int_id, last_updated
            ) VALUES %s
            ON CONFLICT (nocode_int_id) 
            DO UPDATE SET
                name = EXCLUDED.name,
                type = EXCLUDED.type,
                first_year = EXCLUDED.first_year,
                last_year = EXCLUDED.last_year,
                last_updated = EXCLUDED.last_updated
        """,
        'sql_query': "SELECT * FROM Teams",
        'template': "(%s, %s, %s, %s, %s, %s, %s)",
        'field_mapping': {
            'uuid': 'id',
            'fields.team_name': 'name',
            'fields.type_of_team': 'type',
            'fields.year_of_establishment_': 'first_year',
            'fields.last_year': 'last_year',
            'fields.id': 'nocode_int_id',
            'fields.updated_at': 'last_updated'
        },
        'transformations': {
            'uuid': lambda x, ctx: str(uuid.uuid4()) if not x else x,
            'fields.last_year': lambda x, ctx: x if type(x) is not dict else None,
            'fields.updated_at': lambda x, ctx: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S') if x else None,
        },
        'dependencies': []
    },
    {
        'grist_table': 'Participations',
        'insert_query': """
            INSERT INTO participation (
                id, year, role_code, status_code, person_id, direction_id, last_updated, nocode_int_id
            ) VALUES %s
            ON CONFLICT (nocode_int_id) 
            DO UPDATE SET
                year = EXCLUDED.year,
                role_code = EXCLUDED.role_code,
                status_code = EXCLUDED.status_code,
                person_id = EXCLUDED.person_id,
                direction_id = EXCLUDED.direction_id,
                last_updated = EXCLUDED.last_updated,
                nocode_int_id = EXCLUDED.nocode_int_id
        """,
        'sql_query': "SELECT * FROM Participations",
        'template': "(%s, %s, %s, %s, %s, %s, %s, %s)",
        'field_mapping': {
            'uuid': 'id',
            'fields.year': 'year',
            'fields.role': 'role_code',
            'fields.status': 'status_code',
            'fields.person': 'person_id',
            'fields.team': 'direction_id',
            'fields.updated_at': 'last_updated',
            'fields.id': 'nocode_int_id',
        },
        'transformations': {
            'uuid': lambda x, ctx: str(uuid.uuid4()) if not x else x,
            'fields.year': lambda x, ctx: x if isinstance(x, int) and x!= 0 else DELETE_RECORD, #SKIP_RECORD,
            'fields.status': lambda x, ctx: ctx['status_mapping'].get(x, None).get('code', None) if ctx['status_mapping'].get(x, None) != None else DELETE_RECORD,
            'fields.role': lambda x, ctx: ctx['roles_mapping'].get(x, None).get('code',None) if ctx['roles_mapping'].get(x, None) != None else DELETE_RECORD,
            'fields.updated_at': lambda x, ctx: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S') if x else None,
            'fields.person': lambda x, ctx: x if x != 0 and isinstance(x, int) else DELETE_RECORD,
            'fields.team': lambda x, ctx: x if x != 0 and isinstance(x, int) else DELETE_RECORD,
            'fields.to_delete': lambda x, ctx: RESTORE_RECORD if x else False,
        },
        'dependencies': ['People', 'Teams']
    },
    {
        'grist_table': 'People',
        'insert_query': """
            INSERT INTO person (
                id, name, last_name, first_name, nickname, other_names, 
                telegram, phone, email, gender, birth_date, city, comment, 
                nocode_int_id, last_updated
            ) VALUES %s
            ON CONFLICT (nocode_int_id) 
            DO UPDATE SET
                name = EXCLUDED.name,
                last_name = EXCLUDED.last_name,
                first_name = EXCLUDED.first_name,
                nickname = EXCLUDED.nickname,
                other_names = EXCLUDED.other_names,
                telegram = EXCLUDED.telegram,
                phone = EXCLUDED.phone,
                email = EXCLUDED.email,
                gender = EXCLUDED.gender,
                birth_date = EXCLUDED.birth_date,
                city = EXCLUDED.city,
                comment = EXCLUDED.comment,
                last_updated = EXCLUDED.last_updated
        """,
        'sql_query': "SELECT * FROM People",
        'template': "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        'field_mapping': {
            'fields.ntn_id': 'id',
            'fields.name': 'name',
            'fields.last_name': 'last_name',
            'fields.first_name': 'first_name',
            'fields.nickname': 'nickname',
            'fields.other_names': 'other_names',
            'fields.Telegram': 'telegram',
            'fields.phone': 'phone',
            'fields.Email': 'email',
            'fields.gender': 'gender',
            'fields.birth_date': 'birth_date',
            'fields.city': 'city',
            'fields.comment': 'comment',
            'fields.id': 'nocode_int_id',
            'fields.updated_at': 'last_updated'
        },
        'transformations': {
            'fields.ntn_id': lambda x, ctx: str(uuid.uuid4()) if not x else x,
            'fields.birth_date': lambda x, ctx: datetime.fromtimestamp(x).strftime('%Y-%m-%d') if x else None,
            'fields.updated_at': lambda x, ctx: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S') if x else None,
            'fields.other_names': lambda x, ctx: [x] if isinstance(x, str) else x if x else [],
        },
        'dependencies': []
    },
    {
        'grist_table': 'Badges_2025_copy2',#'Badges_2025',
        'insert_query': """
            INSERT INTO badge (
                id, name, last_name, first_name, gender, 
                phone, diet, feed, batch, role_code,
                comment, nocode_int_id, last_updated,
                occupation, person_id, parent_id, photo
            ) VALUES %s
            ON CONFLICT (nocode_int_id) DO UPDATE SET
                name = EXCLUDED.name,
                last_name = EXCLUDED.last_name,
                first_name = EXCLUDED.first_name,
                gender = EXCLUDED.gender,
                phone = EXCLUDED.phone,
                diet = EXCLUDED.diet,
                feed = EXCLUDED.feed,
                batch = EXCLUDED.batch,
                role_code = EXCLUDED.role_code,
                comment = EXCLUDED.comment,
                last_updated = EXCLUDED.last_updated,
                occupation = EXCLUDED.occupation,
                person_id = EXCLUDED.person_id,
                parent_id = EXCLUDED.parent_id,
                photo = EXCLUDED.photo
        """,
        'additional_queries': [
            {
                'insert_query': """
                    -- Удаляем старые связи
                    DELETE FROM badge_directions
                    WHERE badge_id = %s;

                    -- Вставляем новые связи
                    INSERT INTO badge_directions (badge_id, direction_id)
                    SELECT b.nocode_int_id, d.nocode_int_id
                    FROM UNNEST(%s::INT[]) AS grist_direction_id
                    JOIN direction d ON d.nocode_int_id = grist_direction_id
                    CROSS JOIN badge b
                    WHERE b.nocode_int_id = %s;
                """,
                'fields': ['fields.id', 'fields.team_list'],
                'transformations': {
                    'fields.team_list': lambda x, ctx: x if isinstance(x, list) else [],
                }
            }
        ],
        'sql_query': "SELECT * FROM Badges_2025_copy2", #Badges_2025
        'template': "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        'field_mapping': {
            'fields.UUID': 'id',
            'fields.name': 'name',
            'fields.last_name': 'last_name',
            'fields.first_name': 'first_name',
            'fields.gender': 'gender',
            'fields.phone': 'phone',
            'fields.is_vegan': 'diet',
            'fields.feed_type': 'feed',
            'fields.batch': 'batch',
            'fields.role': 'role_code',
            'fields.comment': 'comment',
            'fields.id': 'nocode_int_id',
            'fields.updated_at': 'last_updated',
            'fields.position': 'occupation',
            'fields.person': 'person_id',
            'fields.parent': 'parent_id',
            'fields.photo_attach_id': 'photo'
        },
        'transformations': {
            #'uuid': lambda x, ctx: str(uuid.uuid4()) if not x else x,
            'fields.role': lambda x, ctx: ctx['roles_mapping'].get(x, ctx['roles_mapping'].get(4, {})).get('code', 'VOLUNTEER'),
            'fields.batch': lambda x, ctx: x if isinstance(x, int) else None,
            'fields.updated_at': lambda x, ctx: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S') if x else None,
            'fields.parent': lambda x, ctx: x if x !=0 else None, 
            'fields.person': lambda x, ctx: x if x != 0 else None,
            'fields.photo_attach_id': lambda x, ctx: f"{app_config.grist.server}/api/docs/{app_config.grist.doc_id}/attachments/{x}/download" if x else None
        },
        'dependencies': ['Teams']
    },
    {
        'grist_table': 'Arivals_2025_copy2', #'Arrivals_2025',
        'insert_query': """
            INSERT INTO arrival (
                id, arrival_date, arrival_transport, 
                departure_date, departure_transport, last_updated,  
                status, badge_id, nocode_int_id
            ) VALUES %s
            ON CONFLICT (nocode_int_id) 
            DO UPDATE SET
                arrival_date = EXCLUDED.arrival_date,
                arrival_transport = EXCLUDED.arrival_transport,
                departure_date = EXCLUDED.departure_date,
                departure_transport = EXCLUDED.departure_transport,
                last_updated = EXCLUDED.last_updated,
                status = EXCLUDED.status,
                badge_id = EXCLUDED.badge_id,
                id = EXCLUDED.id
        """,
        'sql_query': "SELECT * FROM Arivals_2025_copy2", #Arrivals_2025
        'template': "(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        'field_mapping': {
            'fields.UUID': 'id',
            'fields.arrival_date': 'arrival_date',
            'fields.arrival_transport': 'arrival_transport',
            'fields.departure_date': 'departure_date',
            'fields.departure_transport': 'departure_transport',
            'fields.updated_at': 'last_updated',
            'fields.status': 'status',
            'fields.badge': 'badge_id',
            'fields.id': 'nocode_int_id',
        },
        'transformations': {
            'fields.UUID': lambda x, ctx: str(uuid.uuid4()) if not x else x,
            'fields.arrival_date': lambda x, ctx: datetime.fromtimestamp(x).strftime('%Y-%m-%d') if x else SKIP_RECORD,
            'fields.departure_date': lambda x, ctx: datetime.fromtimestamp(x).strftime('%Y-%m-%d') if x else SKIP_RECORD,
            'fields.updated_at': lambda x, ctx: datetime.fromtimestamp(x).strftime('%Y-%m-%d') if x else None,
            'fields.status': lambda x, ctx: ctx['status_mapping'].get(x, None).get('code', None),
            'fields.badge': lambda x, ctx: x if isinstance(x, int) and x!= 0 else SKIP_RECORD,
            'fields.arrival_transport': lambda x, ctx: ctx['arrivals_mapping'].get(x, ctx['arrivals_mapping'].get(1, {})).get('code', None), #x if isinstance(x, int) else None,
            'fields.departure_transport': lambda x, ctx: ctx['arrivals_mapping'].get(x, ctx['arrivals_mapping'].get(1, {})).get('code', None), #x if isinstance(x, int) else None
        },
        'dependencies': []
    }
]





