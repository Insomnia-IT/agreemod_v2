FROM python:3.11-slim-bookworm
ENV DEBIAN_FRONTEND=noninteractive

RUN pip3 install --upgrade pip poetry

WORKDIR /opt/app

COPY app app
COPY database database
COPY alembic alembic
COPY dictionaries dictionaries
COPY updater updater

COPY .env alembic.ini alembic/poetry.lock alembic/pyproject.toml ./

RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi --no-root

ENTRYPOINT ["/bin/bash"]