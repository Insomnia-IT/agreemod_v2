FROM python:3.11-slim-bookworm
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /opt/app

# RUN apt update && apt -y install nano curl g++ && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip poetry

COPY .env app/poetry.lock app/pyproject.toml /opt/app/

RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi

EXPOSE 8000
ENTRYPOINT ["python", "-m", "app.main"]