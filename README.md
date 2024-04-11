# agreemod_v2
Интеграция Notion и Coda

### Локальный запуск API
```
uvicorn app.main:get_app --reload
```

### Миграции
Генерация миграций с текущей датой
```
alembic revision --autogenerate --rev-id=`date '+%Y_%m_%d_%H%M'` -m "COMMENT"

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
