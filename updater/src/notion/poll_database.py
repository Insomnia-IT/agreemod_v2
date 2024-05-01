import asyncio
import logging
from typing import Union

import venusian

from sqlalchemy import select

from db.orm import PersonORM, DirectionORM
from db.orm.participation import ParticipationORM
from updater.src.config import config
from updater.src.notion.client import NotionClient
from updater.src.notion.databases import DATABASE_REGISTRY, Directions, Persons, Participations

from db.meta import async_session

logger = logging.getLogger(__name__)


async def poll_database(
        client: NotionClient,
        database: Union[
            Directions,
            Persons,
            Participations,
        ]
):
    venusian.Scanner().scan(__import__("db"))
    response = await client.query_database(database=database, mock=False)  # TODO: read from config / DEBUG
    logger.info(f"Received {database.name} table data")
    async with async_session() as session:
        for item in response:
            model = database.model(notion_id=item.id, **item.properties)

            try:
                # TODO: эта стратегия не полностью работает для таблицы Participation
                orm: Union[
                    ParticipationORM,
                    PersonORM,
                    DirectionORM,
                ] = client.convert_model(model, database.orm)
            except Exception as e:
                logger.error(f"{e.__class__.__name__}: {e}")
                continue

            try:
                exist = await session.scalar(
                    select(database.orm).filter_by(notion_id=orm.notion_id)
                )
                if not exist:
                    session.add(orm)
                else:
                    await session.merge(orm)
            except Exception as e:
                logger.error(f"{e.__class__.__name__}: {e}")
                continue

        await session.commit()
        logger.info("Notion direction table data was stored to db")


if __name__ == "__main__":
    client = NotionClient(token=config.notion.token)
    for name, db in DATABASE_REGISTRY.items():
        asyncio.run(poll_database(client, db()))
