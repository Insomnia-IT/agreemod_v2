# TODO: Switch to Alpine once someone have sufficient mental bandwidth to handle this.
FROM python:3.11-bullseye

WORKDIR /opt/app

RUN pip3 install --upgrade pip poetry

COPY .env updater/poetry.lock updater/pyproject.toml /opt/app/

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

CMD ["bash", "-c", "python -m alembic upgrade head"]
