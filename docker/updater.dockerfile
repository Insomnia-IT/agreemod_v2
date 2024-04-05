FROM python:3.11-slim-bookworm
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /opt/app

RUN pip3 install --upgrade pip poetry

COPY .env updater/poetry.lock updater/pyproject.toml /opt/app/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

ENTRYPOINT ["python", "-m", "updater.main"]