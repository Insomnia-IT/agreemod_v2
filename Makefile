# локальная установка
install:
	python3 -m venv venv && \
	source venv/bin/activate && \
	python -m pip install poetry && \
	python -m poetry install --no-root

#Докер
rebuild: stop down build up

build:
	docker compose build

stop:
	docker compose stop

up:
	docker compose up -d

down:
	docker compose down --remove-orphans

#Миграции
migrate:
	docker compose exec -it alembic poetry run alembic upgrade head

migrate-generate:
	alembic revision --autogenerate --rev-id=`date '+%Y_%m_%d_%H%M'` -m "COMMENT"

migrate-generate-docker:
	docker compose exec -it alembic poetry run alembic revision --autogenerate --rev-id=`date '+%Y_%m_%d_%H%M'` -m "COMMENT"

migrate-down:
	docker compose exec -it alembic poetry run alembic downgrade -1

migrate-up:
	docker compose exec -it alembic poetry run alembic upgrade +1

#Анализатор кода
updater-check-all: updater-flake8 updater-isort updater-black

app-check-all: app-flake8 app-isort app-black

check-all: updater-check-all app-check-all

app-flake8:
	docker compose exec -it agreemod flake8 .

app-isort:
	docker compose exec -it agreemod isort .

app-black:
	docker compose exec -it agreemod black .

updater-flake8:
	docker compose exec -it updater flake8 .

updater-isort:
	docker compose exec -it updater isort .

updater-black:
	docker compose exec -it updater black .