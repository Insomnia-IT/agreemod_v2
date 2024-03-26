import logging
import aio_pika

from interface import RMQConsumerInterface

logger = logging.getLogger(__name__)


class RabbitMQAsyncConsumer(RMQConsumerInterface):
    def __init__(self, queue_name, rabbitmq_url):
        self.queue_name = queue_name
        self.rabbitmq_url = rabbitmq_url

    @staticmethod
    async def callback(message):
        async with message.process():
            decoded_message = message.body.decode()
            logger.info(f"Received message: {decoded_message}")

    async def consume_messages(self):
        try:
            connection = await aio_pika.connect_robust(self.rabbitmq_url)
            logger.info("Connected to RabbitMQ")
            async with connection:
                channel = await connection.channel()
                queue = await channel.declare_queue(self.queue_name, auto_delete=False)

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        await self.callback(message)
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
