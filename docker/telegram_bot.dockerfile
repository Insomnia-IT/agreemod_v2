FROM python:3.11-slim-bookworm
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /opt/app

# RUN apt update && apt -y install nano curl g++ && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip poetry

COPY poetry.lock pyproject.toml /opt/app/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
