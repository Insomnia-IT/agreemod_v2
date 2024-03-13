FROM python:3.11-bullseye

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install

COPY .env /app
COPY . /app

CMD [ "python", "main.py" ]
