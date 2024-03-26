import logging
import aio_pika

logger = logging.getLogger(__name__)


class RabbitMQAsyncPublisher:
    def __init__(self, routing_key, rabbitmq_url):
        self.routing_key = routing_key
        self.rabbitmq_url = rabbitmq_url
        self.connection = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.rabbitmq_url)

    async def close_connection(self):
        if self.connection:
            await self.connection.close()

    async def publish_message(self, message_body):
        if not self.connection:
            await self.connect()

        channel = await self.connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=message_body.encode()),
            routing_key=self.routing_key
        )
        logger.info(f"Published message: {message_body}")
