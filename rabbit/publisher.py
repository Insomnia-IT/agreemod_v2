import json
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

    async def publish_message(self, message_body: dict):
        if not self.connection:
            await self.connect()

        channel = await self.connection.channel()
        encoded_message = json.dumps(message_body).encode()
        await channel.default_exchange.publish(
            aio_pika.Message(body=encoded_message),
            routing_key=self.routing_key
        )
        logger.info(f"Published message: {message_body}")
