import asyncio
from consumer import RabbitMQAsyncConsumer
from publisher import RabbitMQAsyncPublisher

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def send_test_messages(routing_key, rabbitmq_url):
    publisher = RabbitMQAsyncPublisher(routing_key, rabbitmq_url)

    for i in range(5):
        message_body = {"test": i}
        await publisher.publish_message(message_body)
    logger.info("all test messages published")


async def check_rabbitmq():
    queue_name = 'my_queue'
    rabbitmq_url = 'amqp://guest:guest@localhost/'
    routing_key = queue_name

    consumer = RabbitMQAsyncConsumer(queue_name, rabbitmq_url)
    consumer_task = asyncio.create_task(consumer.consume_messages())

    await asyncio.sleep(3)  # Wait for consumer to set up

    await send_test_messages(routing_key, rabbitmq_url)
    logger.info("Test messages sent to RabbitMQ.")

    await asyncio.sleep(1)  # Wait for messages to be processed
    consumer_task.cancel()  # Stop consuming messages


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_rabbitmq())
