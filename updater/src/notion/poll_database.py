import asyncio
import logging
from uuid import uuid4

import venusian
from sqlalchemy import select

from db.meta import async_session
from updater.src.config import config
from updater.src.notion.client import NotionClient
from updater.src.notion.databases import DATABASE_REGISTRY, NotionDatabase
from updater.src.states import UpdaterStates

logger = logging.getLogger(__name__)


class NotionPoller:
    def __init__(self, db: NotionDatabase) -> None:
        self.set_status = {
            'get_people': UpdaterStates.set_people_updater,
            'get_directions': UpdaterStates.set_location_updater,
        }
        self.database = db

    async def __aenter__(self):
        self.set_status[self.database.name](True)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.set_status[self.database.name](False)

    async def poll_database(self, client: NotionClient):
        venusian.Scanner().scan(__import__("db"))
        response = await client.query_database(database=self.database, mock=False)
        logger.info(f"Received {self.database.name} table data")
        async with async_session() as session:
            for item in response:
                model = self.database.model(notion_id=item.id, **item.properties)
                try:
                    orm = client.convert_model(model, self.database.orm)
                except Exception as e:

                    logger.error(f"{e.__class__.__name__}: {e}")
                    continue
                exist = await session.scalar(
                    select(self.database.orm).filter_by(notion_id=orm.notion_id)
                )
                if not exist:
                    orm.id = uuid4()
                    session.add(orm)
                else:
                    orm.id = exist.id
                    await session.merge(orm)
            await session.commit()
            logger.info("Notion direction table data was stored to db")


if __name__ == "__main__":
    client = NotionClient(token=config.notion.token)
    # for name, db in DATABASE_REGISTRY.items():
    #     async with NotionPoller
    #     asyncio.run(poll_database(client, db()))
