FROM python:3.11-slim-bookworm
ENV DEBIAN_FRONTEND=noninteractive

RUN pip3 install --upgrade pip poetry

WORKDIR /opt/app

COPY updater updater
COPY database database
COPY dictionaries dictionaries
COPY rabbit rabbit

COPY .env updater/poetry.lock updater/pyproject.toml ./

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

ENTRYPOINT ["python", "-m", "updater.main_updater"]