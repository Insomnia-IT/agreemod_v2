from updater.src.config import config

from .consumer import UpdaterRabbitConsumer

async def rmq_eat_carrots(updater):
    queue_name = config.rabbitmq.TELEGRAM_QUEUE
    consumer = UpdaterRabbitConsumer(queue_name, config.rabbitmq.rabbitmq_url, updater)
    await consumer.consume_messages()
