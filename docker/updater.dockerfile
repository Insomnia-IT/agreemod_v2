FROM python:3.11-alpine

WORKDIR /opt/app

RUN apk add nano curl g++ && rm -rf /var/cache/apk/*

RUN pip3 install --upgrade pip poetry

COPY .env updater/poetry.lock updater/pyproject.toml /opt/app/

RUN poetry config virtualenvs.in-project true
RUN poetry install --only main --no-interaction --no-ansi