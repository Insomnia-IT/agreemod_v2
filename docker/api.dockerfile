FROM python:3.11-slim-bookworm
ENV DEBIAN_FRONTEND=noninteractive

# RUN apt update && apt -y install nano curl g++ && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip poetry

WORKDIR /opt/app

COPY app app
COPY database database
COPY dictionaries dictionaries

COPY .env app/poetry.lock app/pyproject.toml ./

RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi --no-root

EXPOSE 8000
ENTRYPOINT ["python", "-m", "app.main"]