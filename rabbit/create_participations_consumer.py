import json
import asyncio
import os

import aiohttp
import aio_pika
from dotenv import load_dotenv

from common.logging_setup import setup_logging, get_logger


load_dotenv()

setup_logging("create_participations_consumer")
logger = get_logger("create_participations_consumer")

YEAR = 2026
ORGANIZER_ROLE_ID = 1
DIRECTIONS_TABLE = "Directions2026"


class CreateParticipationsConsumer:
    def __init__(self, rabbitmq_url):
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None
        self.queue = None
        self.grist_server = os.getenv("GRIST__SERVER")
        self.grist_doc_id = os.getenv("GRIST__DOC_ID")
        self.grist_api_key = os.getenv("GRIST__API_KEY")
        self._running = True
        self._processing = False

    async def connect(self):
        """Establish connection to RabbitMQ"""
        while self._running:
            try:
                self.connection = await aio_pika.connect_robust(
                    self.rabbitmq_url,
                    timeout=30,
                    reconnect_interval=5,
                )
                self.channel = await self.connection.channel()
                self.queue = await self.channel.declare_queue("create_participations", durable=True)
                logger.info(f"Successfully connected to RabbitMQ on {self.rabbitmq_url}")
                return
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                await asyncio.sleep(5)

    async def close_connection(self):
        """Close RabbitMQ connection"""
        self._running = False
        if self.connection:
            await self.connection.close()

    async def fetch_records(self, session, table_name, filter_query):
        url = (f"{self.grist_server}/api/docs/{self.grist_doc_id}/sql")
        headers = {"Authorization": f"Bearer {self.grist_api_key}"}
        query = f"SELECT * FROM {table_name} {filter_query}"
        async with session.get(
            url,
            headers=headers,
            params={"q": query},
        ) as resp:
            if resp.status != 200:
                error = await resp.text()
                raise Exception(f"SQL Error ({resp.status}): {error}")
            data = await resp.json()
            return data.get("records", [])

    async def create_participation(self, session, person_id, team_id):
        url = (f"{self.grist_server}/api/docs/{self.grist_doc_id}/tables/Participations/records")
        headers = {"Authorization": f"Bearer {self.grist_api_key}"}
        fields = {
            "year": YEAR,
            "person": person_id,
            "role": ORGANIZER_ROLE_ID,
        }
        if team_id != 0:
            fields["team"] = team_id
        payload = {
            "records": [
                {
                    "fields": fields
                }
            ]
        }
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status not in (200, 201):
                error = await resp.text()
                raise Exception(f"Failed to create participation: {error}")

    async def process_message(self, message: aio_pika.IncomingMessage):
        if self._processing:
            await message.nack(requeue=True)
            return

        self._processing = True
        try:
            async with message.process():
                body = json.loads(message.body.decode())
                direction_id = body.get("id")

                if not direction_id:
                    logger.error(f"Invalid message format: {body}")
                    return

                async with aiohttp.ClientSession() as session:
                    direction_records = await self.fetch_records(
                        session,
                        DIRECTIONS_TABLE,
                        f"WHERE id = {direction_id}",
                    )

                    if not direction_records:
                        logger.warning(f"Direction {direction_id} not found")
                        return

                    direction = direction_records[0]
                    team_id = direction["fields"].get("direction_location26")
                    heads = direction["fields"].get("head26", [])
                    if isinstance(heads, str):
                        heads = [
                            int(x.strip())
                            for x in heads.strip("[]").split(",")
                            if x.strip()
                        ]
                    if not isinstance(heads, list):
                        logger.warning(f"Invalid head26 format for direction {direction_id}")
                        return

                    for person_id in heads:
                        if not isinstance(person_id, int):
                            continue

                        existing = await self.fetch_records(
                            session,
                            "Participations",
                            f"WHERE person = {person_id} "
                            f"AND year = {YEAR} "
                            f"AND team = {team_id}"
                        )
                        if existing:
                            logger.info(f"Participation already exists for person {person_id} and team {team_id}")
                            continue

                        await self.create_participation(
                            session,
                            person_id,
                            team_id,
                        )
                        logger.info(f"Created participation for person {person_id} and team {team_id}")

                        await asyncio.sleep(0.05)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
        finally:
            self._processing = False

    async def start_consuming(self):
        """Start consuming messages"""
        while self._running:
            try:
                await self.connect()
                await self.queue.consume(self.process_message)
                logger.info("Started consuming create participations messages")

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
    rabbitmq_host = os.getenv("RABBITMQ__HOST", "rabbitmq")
    rabbitmq_user = os.getenv("RABBITMQ__USER", "guest")
    rabbitmq_password = os.getenv("RABBITMQ__PASSWORD", "guest")
    rabbitmq_port = os.getenv("RABBITMQ__QUEUE_PORT", "5672")
    rabbitmq_url = f"amqp://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_host}:{rabbitmq_port}/"

    consumer = CreateParticipationsConsumer(rabbitmq_url)

    try:
        await consumer.start_consuming()
    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
    finally:
        await consumer.close_connection()

if __name__ == "__main__":
    asyncio.run(main())
