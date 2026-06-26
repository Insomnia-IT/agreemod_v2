![Workflow Status](https://github.com/Insomnia-IT/agreemod_v2/actions/workflows/deploy.yml/badge.svg)
# agreemod_v2
Интеграция с Grist.
Проект представляет из себя монорепозиторий с сервисами:
- app (fastapi)
- grist_updater (синхронизация данных между Grist и локальной базой)


## Настройка окружения

Перед запуском необходимо создать файл `.env` в корне проекта. Основные переменные:

### Обязательные для всех сервисов

```env
# PostgreSQL
POSTGRES__HOST=postgres
POSTGRES__PORT=5432
POSTGRES__USER=agreemod
POSTGRES__PASSWORD=your_password
POSTGRES__NAME=agreemod

# RabbitMQ
RABBITMQ__DEFAULT_HOST=rabbitmq
RABBITMQ__DEFAULT_USER=guest
RABBITMQ__DEFAULT_PASS=guest
RABBITMQ__QUEUE_PORT=5672

# Grist (для синхронизации)
GRIST__SERVER=https://grist.example.com
GRIST__DOC_ID=your_doc_id
GRIST__API_KEY=your_api_key

# Google
GOOGLE__API_KEY=your_api_key

# API авторизация
API_AUTH_USER=user
API_AUTH_PASSWORD=password
```

### Docker Compose переменные

```env
VOLUME_MOUNT_PREFIX=/opt/app
API_HOST=0.0.0.0
API_PORT=8000
API_PROXY=127.0.0.1:8000
POSTGRES__PROXY=5432
RABBITMQ__WEB_PORT=15672
```

См. `env.example` для полного списка переменных. Можно просто скопировать `env.example` в `.env` и пробить недостающие переменные

---

## Makefile команды

### Виртуальное окружение

- `make install`: Создает виртуальное окружение для разработки и работы с модулями проекта.

## Docker команды

### Управление контейнерами

- `make setup_project`: Полная первичная сборка проекта — сборка, миграции и запуск всех сервисов (build + migrate + up).
- `make rebuild`: Полная пересборка и запуск Docker контейнеров.
- `make build`: Сборка всех Docker контейнеров.
- `make stop`: Остановка всех Docker контейнеров.
- `make up`: Запуск всех Docker контейнеров в фоновом режиме.
- `make down`: Остановка и удаление всех Docker контейнеров, включая "сирот".

## Миграции баз данных

### Alembic миграции

- `make migrate`: Применение последних миграций.
- `make migrate-generate`: Генерация новой миграции на основе изменений в моделях.
- `make migrate-down`: Откат последней миграции.
- `make migrate-up`: Применение следующей миграции.

## Анализаторы кода

### Проверка качества кода

- `make check-all`: Запуск всех проверок качества кода для всех компонентов.
- `make app-check-all`: Запуск всех проверок для компонента `app`.
- `make updater-check-all`: Запуск всех проверок для компонента `updater`.
- `make app-flake8`: Запуск `flake8` для анализа кода в компоненте `app`.
- `make app-isort`: Автоматическое форматирование импортов в компоненте `app`.
- `make app-black`: Автоматическое форматирование кода в компоненте `app` с использованием `black`.
- `make updater-flake8`: Запуск `flake8` для анализа кода в компоненте `updater`.
- `make updater-isort`: Автоматическое форматирование импортов в компоненте `updater`.
- `make updater-black`: Автоматическое форматирование кода в компоненте `updater`.

### Локальный запуск API
```
uvicorn app.main:get_app --reload
```

### Миграции
Генерация миграций с текущей датой
```
alembic revision --autogenerate -m "create audit log table"

```
Апгрейд вперёд до последней версии
```
alembic upgrade head
```

Апгрейд вперёд на 1 миграцию
```
alembic upgrade +1
```

Откат назад
```
alembic downgrade -1
```

## Архитектура и функционал сервисов

### FastAPI приложение (`app`)

REST API сервис, предоставляющий endpoints для работы с данными:

- **Бейджи** (`/badges`) - управление бейджами участников с фильтрацией по партии, цвету, службе, роли
- **Заезды** (`/arrivals`) - информация о заездах участников
- **Люди** (`/people`) - управление персональными данными
- **Направления** (`/places`) - управление службами (directions/teams)
- **Feeder API** (`/feeder/*`) - интеграция с системой "кормитель":
  - `GET /feeder/sync` - получение изменений с указанной даты (для синхронизации с внешней системой)
  - `POST /feeder/back-sync` - обратная синхронизация данных из внешней системы в PostgreSQL
- **Синхронизация фото** (`/photo-sync`) - синхронизация фотографий из Google Drive в Grist:
  - `POST /photo-sync/{record_id}` - синхронизация фотографий для одной серии `Import_series`
  - `POST /photo-sync` - массовая синхронизация всех серий с агрегацией результатов

### Grist Updater (`grist_updater`)

Сервис для синхронизации данных между Grist и PostgreSQL. Работает непрерывно в цикле:

**Частота работы:** каждые 30 секунд

**Что делает:**
1. Получает изменения из таблиц Grist (Teams, People, Participations, Badges_2026, Arrivals_2026) с момента последней синхронизации
2. Трансформирует данные согласно маппингу полей и валидации
3. Вставляет/обновляет записи в PostgreSQL
4. Сохраняет состояние синхронизации в таблице `sync_state`
5. Проверяет изменения в `Directions2026` и отправляет сообщения в очередь `create_participations`

**Обработка ошибок:**
- При ошибках синхронизации используется retry с экспоненциальным backoff (до 3 попыток для цикла, до 5 для таблицы)
- При превышении лимита попыток сервис продолжает работу со следующей итерацией

**Удаление и восстановление записей:**
- Если запись не проходит валидацию (например, пустое имя), updater отправляет сообщение в RabbitMQ в очередь `delete_records`
- Если запись помечена в Grist флагом `to_delete`, она также отправляется в `delete_records`
- Если флаг `to_delete` снят, отправляется сообщение в очередь `restore_records`

**Перезапуск:**
- Сервис автоматически перезапускается каждый день в 00:00 через `restarter` контейнер

### RabbitMQ Consumers

#### Delete Consumer (`delete_consumer`)

Слушает очередь `delete_records`:
- Получает сообщения с `table_name`, `id` и `reason`
- Обновляет запись в Grist: устанавливает `to_delete` = timestamp и `delete_reason`
- Обновляет запись в PostgreSQL: устанавливает `deleted` = TRUE
- Работает последовательно (одно сообщение за раз) с задержкой 50мс между запросами

#### Restore Consumer (`restore_consumer`)

Слушает очередь `restore_records`:
- Получает сообщения с `table_name` и `id`
- Очищает поле `to_delete` в Grist (устанавливает в NULL)
- Обновляет запись в PostgreSQL: устанавливает `deleted` = FALSE
- Работает последовательно с задержкой 50мс между запросами

#### Create Participations Consumer (`create_participations_consumer`)

Слушает очередь `create_participations`:
- Получает сообщения с `id` направления из `Directions2026`
- Получает список организаторов из поля `head26`
- Проверяет наличие участия (`Participations`) для организатора
- Если участие отсутствует - создаёт его автоматически
- При создании участия используетcя id человека из поля `head26`, текущий год, роль организатора и команду из поля `direction_location26`
- Работает последовательно с задержкой 50мс между запросами

**Когда отправляются сообщения:**
- **Delete:** когда в API или updater выявляется невалидная запись (пустые обязательные поля, некорректные связи)
- **Restore:** когда в Grist снимается флаг удаления (`to_delete` очищается)
- **Create Participations:** когда изменяется запись в `Directions2026`

### Feeder Sync (`GET /feeder/sync`)

Прямая синхронизация данных из PostgreSQL во внешнюю систему ("кормитель"):

1. Внешняя система запрашивает данные с указанной даты (`from_date` в формате UTC)
2. API извлекает из PostgreSQL все записи, измененные с указанной даты:
   - Бейджи (badges)
   - Заезды (arrivals)
   - Участия (engagements/participations)
   - Персоны (persons)
   - Направления (directions)
3. Данные сериализуются и возвращаются в ответе

**Использование:** Внешние системы вызывают этот endpoint для получения актуальных данных из agreemod.

### Бэк-синк (Back-sync)

Процесс обратной синхронизации данных из внешних систем (например, "кормителя") **напрямую в Grist**:

1. Внешняя система отправляет данные через `POST /feeder/back-sync`
2. Данные обогащаются связанными сущностями из PostgreSQL (person, directions)
3. **Записи создаются или обновляются напрямую в Grist** через API:
   - `badge_to_grist.py` - синхронизация бейджей
   - `arrivals_to_grist.py` - синхронизация заездов
4. Grist Updater при следующей итерации (в течение 30 секунд) забирает изменения из Grist и синхронизирует их с PostgreSQL

**Использование:** Внешние системы отправляют изменения, которые должны попасть в agreemod. Данные сначала попадают в Grist, затем через grist_updater в PostgreSQL.

---

## Структура моделей и маппинг Grist → PostgreSQL

Ниже описана каждая модель (таблица PostgreSQL), её назначение и то, из каких колонок Grist собираются её поля. ORM-модели описаны в [`database/orm/`](database/orm/), конфигурация синхронизации — в [`grist_updater/grist_updater.py`](grist_updater/grist_updater.py) (константа `TABLES_CONFIG`).

### Ключевые принципы маппинга

- **`nocode_int_id`** — целочисленный идентификатор записи из Grist (`fields.id`). Это «якорь» синхронизации: все upsert-операции идут через `ON CONFLICT (nocode_int_id)`, и связи между таблицами (FK) строятся именно по нему, а не по UUID.
- **`id` (UUID)** — внутренний первичный ключ PostgreSQL. Берётся из колонки Grist (`UUID` / `ntn_id`), а если она пуста — генерируется новый `uuid.uuid4()`.
- **`last_updated`** — всегда перезаписывается текущим временем сервера (МСК, UTC+3) в момент синхронизации, а не значением из Grist.
- **Инкрементальная выборка** — из Grist забираются только записи с `updated_at >= last_sync - 300с` (с запасом в 5 минут); состояние хранится в таблице `sync_state`.
- **Валидация и удаление** — если трансформация поля возвращает `DELETE_RECORD`, запись отправляется в очередь `delete_records` (см. раздел RabbitMQ Consumers); `SKIP_RECORD` — запись просто пропускается; флаг `to_delete` в Grist управляет удалением/восстановлением.
- **Справочники** (`participation_role`, `participation_status`) подгружаются отдельно из таблиц Grist `Roles` и `Participation_statuses`; в основных таблицах хранятся не Grist-id справочника, а его текстовый `code`.

### `direction` — Направления / службы (Grist: `Teams`)

Служба или локация мероприятия.

| Колонка PostgreSQL | Колонка Grist (`Teams`) | Преобразование |
|---|---|---|
| `id` (UUID) | `UUID` | если пусто — генерируется новый UUID |
| `name` | `team_name` | обязательное; пустое → `DELETE_RECORD` |
| `type` (FK → `direction_type.name`) | `type_of_team` | обязательное; пустое → `DELETE_RECORD` |
| `first_year` | `year_of_establishment_` | |
| `last_year` | `last_year` | dict-значение → `NULL` |
| `nocode_int_id` | `id` | |
| `last_updated` | `updated_at` | заменяется на текущее время сервера |

### `person` — Люди (Grist: `People`)

Персональные данные человека.

| Колонка PostgreSQL | Колонка Grist (`People`) | Преобразование |
|---|---|---|
| `id` (UUID) | `ntn_id` | если пусто — генерируется новый UUID |
| `name` | `name` | обязательное; пустое → `DELETE_RECORD` |
| `last_name` | `last_name` | |
| `first_name` | `first_name` | |
| `nickname` | `nickname` | |
| `other_names` (ARRAY) | `other_names` | приводится к Postgres-массиву; при наличии `{`, `}`, `"` → `NULL` |
| `telegram` | `Telegram` | |
| `phone` | `phone` | |
| `email` | `Email` | |
| `gender` | `gender` | допускаются только `М`, `Ж`, `др.`, иначе `NULL` |
| `birth_date` | `birth_date` | timestamp → `YYYY-MM-DD` |
| `city` | `city` | |
| `comment` | `comment` | |
| `nocode_int_id` | `id` | |
| `banned` | `isInBL` | `Нет`/пусто → `False`, иначе `True` |
| `last_updated` | `updated_at` | заменяется на текущее время сервера |

### `participation` — Участия (Grist: `Participations`)

Связь человека со службой в конкретном году с ролью и статусом. SQL-выборка из Grist делает `JOIN` с `People` и `Teams`, чтобы провалидировать связанные сущности.

| Колонка PostgreSQL | Колонка Grist (`Participations`) | Преобразование |
|---|---|---|
| `id` (UUID) | `UUID` | если пусто — генерируется новый UUID |
| `year` | `year` | целое и ≠ 0, иначе `DELETE_RECORD` |
| `role_code` (FK → `participation_role.code`) | `role` | Grist-id → `code` через `roles_mapping`; нет соответствия → `DELETE_RECORD` |
| `status_code` (FK → `participation_status.code`) | `status` | Grist-id → `code` через `status_mapping`; нет соответствия → `DELETE_RECORD` |
| `person_id` (FK → `person.nocode_int_id`) | `person` | целое и ≠ 0, иначе `DELETE_RECORD` |
| `direction_id` (FK → `direction.nocode_int_id`) | `team` | целое и ≠ 0, иначе `DELETE_RECORD` |
| `nocode_int_id` | `id` | |
| `last_updated` | `updated_at` | заменяется на текущее время сервера |

Дополнительные проверки по JOIN-полям: пустое имя человека, имя команды или тип команды → `DELETE_RECORD`. Зависит от таблиц `People` и `Teams` (синхронизируются раньше).

### `badge` — Бейджи (Grist: `Badges_2026`)

Бейдж участника на конкретный год.

| Колонка PostgreSQL | Колонка Grist (`Badges_2026`) | Преобразование |
|---|---|---|
| `id` (UUID) | `UUID` | если пусто — генерируется новый UUID |
| `name` | `name` | обязательное; пустое/не-строка → `DELETE_RECORD` |
| `last_name` | `last_name` | не-строка → `NULL` |
| `first_name` | `first_name` | не-строка → `NULL` |
| `gender` | `gender` | только значения из справочника `Gender`, иначе `NULL` |
| `phone` | `phone` | |
| `diet` | `diet` | обязательное; пустое → `DELETE_RECORD` |
| `feed` | `feed_type` | только значения из `FeedType`, иначе `DELETE_RECORD` |
| `batch` | `batch` | не-int → `NULL` |
| `role_code` (FK → `participation_role.code`) | `role` | Grist-id → `code` через `roles_mapping`; нет соответствия → `DELETE_RECORD` |
| `comment` | `comment` | |
| `nocode_int_id` | `id` | |
| `occupation` | `position` | не-строка → `NULL` |
| `person_id` (FK → `person.nocode_int_id`) | `person` | целое и ≠ 0, иначе `NULL` |
| `photo` | `photo_attach_id` | преобразуется в URL вложения Grist |
| `child` | `infant` | приводится к bool |
| `number` | `number` | не-строка → `NULL` |
| `ticket` | `ticket` | приводится к bool |
| `last_updated` | `updated_at` | заменяется на текущее время сервера |

Дополнительно (`additional_queries`):
- **`badge_directions`** — связь бейджа со службами: из `directions_ref` (список Grist-id) пересобираются строки `(badge_id, direction_id)` по `nocode_int_id`.
- **`parent_id`** — иерархия бейджей: из поля `parent` проставляется ссылка на родительский бейдж (0/не-int → `NULL`).
- Запись с `delete_reason`, содержащим `FEEDER`, пропускается (`SKIP_RECORD`), чтобы не перетирать данные из back-sync. Зависит от таблицы `Teams`.

### `arrival` — Заезды (Grist: `Arrivals_2026`)

Информация о заезде/отъезде по бейджу. SQL-выборка делает `JOIN` с `Badges_2026` для валидации бейджа.

| Колонка PostgreSQL | Колонка Grist (`Arrivals_2026`) | Преобразование |
|---|---|---|
| `id` (UUID) | `UUID` | если пусто — генерируется новый UUID |
| `arrival_date` | `arrival_date` | timestamp → `YYYY-MM-DD`; пусто → `DELETE_RECORD` |
| `arrival_transport` (FK → `transport_type.code`) | `arrival_transport` | Grist-id → `code` через `arrivals_mapping` (по умолчанию id=1) |
| `departure_date` | `departure_date` | timestamp → `YYYY-MM-DD`; пусто → `DELETE_RECORD` |
| `departure_transport` (FK → `transport_type.code`) | `departure_transport` | Grist-id → `code` через `arrivals_mapping` (по умолчанию id=1) |
| `status` (FK → `participation_status.code`) | `status` | Grist-id → `code` через `status_mapping`; нет соответствия → `DELETE_RECORD` |
| `badge_id` (FK → `badge.nocode_int_id`) | `badge` | целое и ≠ 0, иначе `DELETE_RECORD` |
| `nocode_int_id` | `id` | |
| `last_updated` | `updated_at` | заменяется на текущее время сервера |

Если у связанного бейджа `delete_reason` содержит `FEEDER` или бейдж не прошёл валидацию (имя/диета/feed/роль) — заезд помечается `DELETE_RECORD`.

### Справочники (загружаются отдельно)

| Таблица PostgreSQL | Таблица Grist | Поля |
|---|---|---|
| `participation_role` | `Roles` | `code` ← `Code`, `name` ← `Name` |
| `participation_status` | `Participation_statuses` | `code` ← `code`, `name` ← `A`, `to_list` ← `to_list`, `comment` ← `B` |
| `transport_type` | `Arrival_type` | `code` ← `code`, `name` ← `title` (используется как `arrivals_mapping`) |

### Порядок синхронизации

Таблицы обрабатываются с учётом зависимостей (топологическая сортировка по полю `dependencies`): сначала `Teams` и `People`, затем `Participations` (зависит от обеих), `Badges_2026` (зависит от `Teams`) и `Arrivals_2026`. Отдельно отслеживается таблица `Directions2026` — её изменения порождают сообщения в очередь `create_participations`.