FROM python:3.11-slim

WORKDIR /opt/app

# Install poetry
RUN pip install --upgrade poetry

# Copy poetry files
COPY rabbit rabbit

COPY .env rabbit/poetry.lock rabbit/pyproject.toml ./

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi --no-root

# Run the consumer
CMD ["python", "-m", "rabbit.restore_consumer"] 