import asyncio
import logging

import pydantic
import venusian

from app.db.meta import async_session
from app.db.repos.person import PersonRepo
from updater.config import config
from updater.notion.client import NotionClient
from updater.notion.models.person import Person as NotionPerson


logger = logging.getLogger(__name__)


class NotionDatabase(pydantic.BaseModel):
    id: str = "c565f5fca2df40628cd91cfd59da4a9d"  # TODO: move to enum?
    name: str = "person"


async def poll_notion_person(client: NotionClient):
    venusian.Scanner().scan(__import__("app"))

    database = NotionDatabase()
    response = await client.query_database(database=database, mock=False)

    logger.info("Received notion persons table data")
    async with async_session() as session:
        repo = PersonRepo(session)
        for item in response:
            notion_person = NotionPerson(notion_id=item.id, **item.properties)
            exist = await repo.retrieve(notion_person.notion_id.hex)
            if not notion_person.name:
                continue
            if not exist:
                await repo.create(notion_person)
            else:
                await repo.update(notion_person)
        await session.commit()
        logger.info("Notion direction table data was stored to db")


if __name__ == "__main__":
    client = NotionClient(token=config.notion.token)
    asyncio.run(poll_notion_person(client))
