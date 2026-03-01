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

### Grist Updater (`grist_updater`)

Сервис для синхронизации данных между Grist и PostgreSQL. Работает непрерывно в цикле:

**Частота работы:** каждые 30 секунд

**Что делает:**
1. Получает изменения из таблиц Grist (Teams, People, Participations, Badges_2025, Arrivals_2025) с момента последней синхронизации
2. Трансформирует данные согласно маппингу полей и валидации
3. Вставляет/обновляет записи в PostgreSQL
4. Сохраняет состояние синхронизации в `sync_state.json`

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

**Когда отправляются сообщения:**
- **Delete:** когда в API или updater выявляется невалидная запись (пустые обязательные поля, некорректные связи)
- **Restore:** когда в Grist снимается флаг удаления (`to_delete` очищается)

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