from app.config import Config

from .consumer import UpdaterRabbitConsumer


async def rmq_eat_carrots(updater):
    config = Config()
    queue_name = config.rabbitmq.telegram_queue
    rabbitmq_url = f"amqp://{config.rabbitmq.user}:{config.rabbitmq.password}@{config.rabbitmq.host}/"  # TODO: move to conf

    consumer = UpdaterRabbitConsumer(queue_name, rabbitmq_url, updater)
    await consumer.consume_messages()
