FROM python:3.11-slim-bookworm

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/opt/app

COPY ../bot/poetry.lock ../bot/pyproject.toml /opt/app/
COPY ../bot bot
COPY ../app app
COPY ../database database
COPY ../dictionaries dictionaries
COPY ../rabbit rabbit

RUN pip install --no-cache-dir --upgrade pip poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root --only main

WORKDIR /opt/app/bot
ENTRYPOINT ["python", "-m", "main"]
