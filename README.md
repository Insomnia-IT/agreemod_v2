![Workflow Status](https://github.com/Insomnia-IT/agreemod_v2/actions/workflows/deploy.yml/badge.svg)
# agreemod_v2
Интеграция Notion и Coda.
Проект представляет из себя монорепозиторий с сервисами:
- app (fastapi)
- updater (синхронизация данных между Coda и Notion)
- bot (бот для запуска updater в ручном режиме)


## Makefile команды

### Виртуальное окружение

- `make install`: Создает виртуальное окружение для разработки и работы с модулями проекта.

## Docker команды

### Управление контейнерами

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
