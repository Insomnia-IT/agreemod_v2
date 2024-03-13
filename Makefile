run-db:
	docker compose -f docker-compose.yml up -d

stop-db:
	docker compose -f docker-compose.yml down

run:
	cd app && poetry run python -m app.main

migrate:
	cd app && poetry run alembic upgrade head

flake8:
	flake8 app updater

isort:
	isort app updater

black:
	black app updater

check-all: isort black flake8