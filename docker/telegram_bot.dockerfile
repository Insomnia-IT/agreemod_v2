FROM python:3.11-slim-bookworm

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/opt/app

COPY .env bot/poetry.lock bot/pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root --only main

ENTRYPOINT ["python", "-m", "bot.main"]
