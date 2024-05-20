FROM python:3.11-slim-bookworm
ENV DEBIAN_FRONTEND=noninteractive

RUN pip3 install --upgrade pip poetry

WORKDIR /opt/app

COPY database database
COPY dictionaries dictionaries

COPY .env updater/poetry.lock updater/pyproject.toml ./
COPY updater updater

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

ENTRYPOINT ["python", "-m", "updater.main"]