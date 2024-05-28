FROM python:3.11-slim-bookworm

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY poetry.lock pyproject.toml /opt/app/

RUN pip install --no-cache-dir --upgrade pip poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root --only main

COPY . /opt/app
ENV PYTHONPATH=/opt/app

COPY ../rabbit /opt/app
COPY ../database /opt/app

ENTRYPOINT ["python", "-m", "main"]
