import json
import logging
import asyncio
from datetime import datetime
import aio_pika
import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(module)s] [%(levelname)s]: %(message)s",
    datefmt="%Y.%m.%d %H:%M:%S",
)

# Set RabbitMQ related loggers to WARNING level
logging.getLogger("aio_pika").setLevel(logging.WARNING)
logging.getLogger("aiormq").setLevel(logging.WARNING)
logging.getLogger("connection").setLevel(logging.WARNING)
logging.getLogger("channel").setLevel(logging.WARNING)
logging.getLogger("exchange").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

class DeleteMessageConsumer:
    def __init__(self, rabbitmq_url):
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None
        self.queue = None
        self.grist_server = os.getenv('GRIST__SERVER')
        self.grist_doc_id = os.getenv('GRIST__DOC_ID')
        self.grist_api_key = os.getenv('GRIST__API_KEY')
        self._running = True
        self._processing = False

    async def connect(self):
        """Establish connection to RabbitMQ"""
        while self._running:
            try:
                self.connection = await aio_pika.connect_robust(
                    self.rabbitmq_url,
                    timeout=30,
                    reconnect_interval=5
                )
                self.channel = await self.connection.channel()
                self.queue = await self.channel.declare_queue("delete_records", durable=True)
                logger.info("Successfully connected to RabbitMQ")
                return
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                await asyncio.sleep(5)

    async def close_connection(self):
        """Close RabbitMQ connection"""
        self._running = False
        if self.connection:
            await self.connection.close()

    async def process_message(self, message: aio_pika.IncomingMessage):
        """Process incoming delete message"""
        if self._processing:
            # If we're already processing a message, reject this one and requeue
            await message.nack(requeue=True)
            return

        self._processing = True
        try:
            async with message.process():
                body = json.loads(message.body.decode())
                table_name = body.get('table_name')
                record_id = body.get('id')

                if not table_name or not record_id:
                    logger.error(f"Invalid message format: {body}")
                    return

                # Update Grist record with to_delete timestamp
                url = f"{self.grist_server}/api/docs/{self.grist_doc_id}/tables/{table_name}/records"
                headers = {"Authorization": f"Bearer {self.grist_api_key}"}
                
                update_data = {
                    "records": [{
                        "id": record_id,
                        "fields": {
                            "to_delete": datetime.now().timestamp()
                        }
                    }]
                }

                async with aiohttp.ClientSession() as session:
                    async with session.patch(url, headers=headers, json=update_data) as resp:
                        if resp.status != 200:
                            error = await resp.text()
                            logger.error(f"Failed to update Grist record: {error}")
                        else:
                            logger.info(f"Successfully marked record {record_id} for deletion in {table_name}")

                # Add a delay between requests to avoid overwhelming Grist
                await asyncio.sleep(0.05)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
        finally:
            self._processing = False

    async def start_consuming(self):
        """Start consuming messages"""
        print("Starting to consume delete messages")
        while self._running:
            try:
                await self.connect()
                await self.queue.consume(self.process_message)
                logger.info("Started consuming delete messages")
                print("Completed initialization of consuming delete messages")
                
                # Keep the connection alive
                while self._running and self.connection and not self.connection.is_closed:
                    await asyncio.sleep(0.01)
                
                if self._running:
                    logger.warning("Connection lost, attempting to reconnect...")
                    await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Error in consumer loop: {e}")
                if self._running:
                    await asyncio.sleep(5)

async def main():
    # Construct RabbitMQ URL from environment variables
    rabbitmq_host = os.getenv('RABBITMQ__HOST', 'rabbitmq')
    rabbitmq_user = os.getenv('RABBITMQ__USER', 'guest')
    rabbitmq_password = os.getenv('RABBITMQ__PASSWORD', 'guest')
    rabbitmq_port = os.getenv('RABBITMQ__QUEUE_PORT', '5672')
    rabbitmq_url = f"amqp://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_host}:{rabbitmq_port}/"

    consumer = DeleteMessageConsumer(rabbitmq_url)
    
    try:
        await consumer.start_consuming()
    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
    finally:
        await consumer.close_connection()

if __name__ == "__main__":
    asyncio.run(main()) 