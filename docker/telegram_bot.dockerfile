FROM python:3.11-slim-bookworm

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

COPY ../bot/poetry.lock bot/pyproject.toml /opt/app/

RUN pip install --no-cache-dir --upgrade pip poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root --only main

ENV PYTHONPATH=/opt/app

# ???
COPY ../bot /opt/app
COPY ../db /opt/app
COPY ../rabbit /opt/app

ENTRYPOINT ["python", "-m", "main"]
