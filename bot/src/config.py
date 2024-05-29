from aiogram import Bot
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from rabbit.publisher import RabbitMQAsyncPublisher


class RabbitMQ(BaseSettings):
    host: str = "localhost"
    user: str = "guest"
    password: str = "guest"
    web_port: int = 15672
    queue_port: int = 5672
    telegram_queue: str = "telegram"
    link: str = f"amqp://{password}:{password}@{host}/"

    model_config = SettingsConfigDict(extra="ignore")


class Config(BaseSettings):
    rabbitmq: RabbitMQ

    TELEBOT_TOKEN: str = ""

    API_PREFIX: str = "/api/v1"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
    )

config = Config()

queue_name = config.rabbitmq.telegram_queue
publisher = RabbitMQAsyncPublisher(queue_name, config.rabbitmq.link)

bot = Bot(token=config.TELEBOT_TOKEN)
