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

import json
from pathlib import Path

class GristSync:
    def __init__(self, state_file='sync_state.json'):
        self.status_mapping: Dict[int, str] = {}  # {grist_status_id: status_code}
        self.roles: List[str] = []
        self.badges_map: Dict[int, str] = {}
        self.roles_mapping: Dict[str, str] = {}
        self.state_file = Path(state_file)
        self.last_sync = self._load_sync_state()

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
        if table_name == 'Participations' and last_sync:
            where_clause += " AND (year >= 2024)"
        elif table_name == 'Participations':
            where_clause = "WHERE (year >= 2024)"
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
             p['id']: p['fields'].get('code', None)
            for p in participations
        }
        print(self.status_mapping)

        roles = await self.fetch_grist_table('Roles')
        self.roles_mapping = {
            p['id']: {
                "code":p['fields']['Code'],
                "name":p['fields']['Name']}
            for p in roles
        }
        try:
            await self._insert_roles()
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

    async def sync_table(self, config: Dict):
        """Основной метод синхронизации для одной таблицы"""
        records = await self.fetch_grist_data(config['grist_table'])
        records = records.get('records')

        if config['grist_table'] == 'Participations':
            records = [
                record for record in records
                if record['fields'].get('person', 0) != 0 
                and record['fields'].get('team', 0) != 0
                and record['fields'].get('role_old') != ''
            ]
        
        if not records:
            return
        
        context = {
            "status_mapping": self.status_mapping,
            "roles_mapping": self.roles_mapping,
            "badges_map": self.badges_map,
            "roles": self.roles
        }

        # Преобразование данных
        transformed = [
            self._transform_record(record, config['field_mapping'], config.get('transformations'), context)
            for record in records
        ]

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
                            team_list_raw = self._get_nested_value(record, 'fields.team_list') or []

                            if isinstance(team_list_raw, str):
                                team_list = list(map(int, team_list_raw.strip('[]').split(',')))
                            else:
                                team_list = team_list_raw

                            # Преобразуем список в строку формата PostgreSQL ARRAY
                            team_list_str = "{" + ",".join(map(str, team_list)) + "}"

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
            'fields.status': lambda x, ctx: ctx['status_mapping'].get(x, None),
            'fields.role': lambda x, ctx: ctx['roles_mapping'].get(x, ctx['roles_mapping'].get(4, {})).get('code', 'VOLUNTEER'),
            'fields.updated_at': lambda x, ctx: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S') if x else None,
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
            'fields.other_names': lambda x, ctx: [x] if isinstance(x, str) else x if x else []
        },
        'dependencies': []
    },
    {
        'grist_table': 'Badges_2025',
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
        'sql_query': "SELECT * FROM Badges_2025",
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
            'fields.updated_at': lambda x, ctx: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S') if x else None,
            'fields.parent': lambda x, ctx: x if x !=0 else None,
            'fields.person': lambda x, ctx: x if x != 0 else None,
            'fields.photo_attach_id': lambda x, ctx: f"{app_config.grist.server}/api/docs/{app_config.grist.doc_id}/attachments/{x}/download" if x else None
        },
        'dependencies': ['Teams']
    },
    {
        'grist_table': 'Arrivals_2025',
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
                badge_id = EXCLUDED.badge_id
        """,
        'sql_query': "SELECT * FROM Arrivals_2025",
        'template': "(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        'field_mapping': {
            'uuid': 'id',
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
            'uuid': lambda x, ctx: str(uuid.uuid4()) if not x else x,

            'fields.arrival_date': lambda x, ctx: datetime.fromtimestamp(x).strftime('%Y-%m-%d') if x else None,
            'fields.departure_date': lambda x, ctx: datetime.fromtimestamp(x).strftime('%Y-%m-%d') if x else None,
            'fields.updated_at': lambda x, ctx: datetime.fromtimestamp(x).strftime('%Y-%m-%d') if x else None,
            'fields.status': lambda x, ctx: ctx['status_mapping'].get(x, None)
        },
        'dependencies': []
    }
]





