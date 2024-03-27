import json
import logging
import aio_pika

from .interface import RMQConsumerInterface

logger = logging.getLogger(__name__)


class RabbitMQAsyncConsumer(RMQConsumerInterface):
    def __init__(self, queue_name, rabbitmq_url):
        self.queue_name = queue_name
        self.rabbitmq_url = rabbitmq_url
        self.connection = None

    async def connect(self):
        if not self.connection:
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            logger.info("Connected to RabbitMQ")

    async def close_connection(self):
        if self.connection:
            await self.connection.close()
            self.connection = None
            logger.info("Connection to RabbitMQ closed")

    @staticmethod
    async def callback(message):
        try:
            async with message.process() as msg:
                decoded_msg: str = msg.body.decode()
                json_message = json.loads(decoded_msg)
                logger.info(f"Processed message: {json_message}")
                return json_message

        except Exception as e:
            logger.error(f"unable to process message: {e}")

    async def consume_messages(self):
        try:
            await self.connect()

            async with self.connection:
                channel = await self.connection.channel()
                queue = await channel.declare_queue(self.queue_name, auto_delete=False)
                await queue.purge()  # TODO: to do or not to do?

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        await self.callback(message)

        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
