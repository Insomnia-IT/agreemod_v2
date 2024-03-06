run-db:
	docker compose -f docker-compose_local_db.yml up -d

stop-db:
	docker compose -f docker-compose_local_db.yml down

run:
	poetry run python -m app.main

migrate:
	poetry run alembic upgrade head

flake8:
	poetry run flake8 app updater

isort:
	poetry run isort app updater

black:
	poetry run black app updater

check-all: isort black flake8