import asyncio
import logging

import pydantic
import venusian

from updater.src.config import config
from updater.src.notion import Direction as NotionDirection
from updater.src.notion import NotionClient

from app.models.direction import Direction
from db.meta import async_session
from db.repos.direction import DirectionRepo


logger = logging.getLogger(__name__)


class NotionDatabase(pydantic.BaseModel):
    id: str = "0755cd9bb4ee4c09b70a2602f5ad6590"
    name: str = "directions"


async def poll_notion_directions(client: NotionClient):
    venusian.Scanner().scan(__import__("app"))

    database = NotionDatabase()
    response = await client.query_database(database=database)

    logger.info("Received notion directions table data")
    async with async_session() as session:
        repo = DirectionRepo(session)
        for item in response:
            notion_direction = NotionDirection(notion_id=item.id, **item.properties)
            try:
                data = client.convert_model(notion_direction, Direction)
            except pydantic.ValidationError as e:
                logger.error(e.errors())
            exist = await repo.retrieve(data.notion_id.hex)
            if exist is None:
                await repo.create(data)
            else:
                await repo.update(data)
        await session.commit()
        logger.info("Notion direction table data was stored to db")


if __name__ == "__main__":
    client = NotionClient(token=config.notion.token)
    asyncio.run(poll_notion_directions(client))
