FROM python:3.11-slim-bookworm
ENV DEBIAN_FRONTEND=noninteractive

RUN pip3 install --upgrade pip poetry virtualenv

WORKDIR /opt/app

COPY grist_updater grist_updater
COPY database database
COPY dictionaries dictionaries
COPY rabbit rabbit

COPY .env grist_updater/poetry.lock grist_updater/pyproject.toml ./

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi  --no-root

ENTRYPOINT ["python", "-m", "grist_updater.run_updater"]
