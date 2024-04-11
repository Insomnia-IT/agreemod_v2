import asyncio
import logging

import venusian

from sqlalchemy import select
from updater.config import config
from updater.notion.client import NotionClient
from updater.notion.databases import DATABASE_REGISTRY, NotionDatabase

from db.meta import async_session


logger = logging.getLogger(__name__)


async def poll_database(client: NotionClient, database: NotionDatabase):
    venusian.Scanner().scan(__import__("db"))
    response = await client.query_database(database=database, mock=False)
    logger.info(f"Received {database.name} table data")
    async with async_session() as session:
        for item in response:
            model = database.model(notion_id=item.id, **item.properties)
            try:
                orm = client.convert_model(model, database.orm)
            except Exception as e:

                logger.error(f"{e.__class__.__name__}: {e}")
                continue
            exist = await session.scalar(
                select(database.orm).filter_by(notion_id=orm.notion_id)
            )
            if not exist:
                session.add(orm)
            else:
                await session.merge(orm)
        await session.commit()
        logger.info("Notion direction table data was stored to db")


if __name__ == "__main__":
    client = NotionClient(token=config.notion.token)
    for name, db in DATABASE_REGISTRY.items():
        asyncio.run(poll_database(client, db()))
