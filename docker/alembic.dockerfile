FROM python:3.11-slim-bookworm
ENV DEBIAN_FRONTEND=noninteractive

RUN pip3 install --upgrade pip poetry

WORKDIR /opt/app

COPY .env alembic.ini alembic/poetry.lock alembic/pyproject.toml ./

RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi

ENTRYPOINT ["/bin/bash"]