from .consumer import UpdaterRabbitConsumer


async def rmq_eat_carrots(updater):
    queue_name = "telegram"  # TODO: read from ini / or .env?
    rabbitmq_url = "amqp://guest:guest@localhost/"

    consumer = UpdaterRabbitConsumer(queue_name, rabbitmq_url, updater)
    await consumer.consume_messages()
