import asyncio
import logging
from typing import Union

import venusian

from sqlalchemy import select

from db.orm import PersonORM, DirectionORM
from db.orm.participation import ParticipationORM
from db.repo.logs import LogsRepository
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
        log_repo = LogsRepository(session)

        for item in response:
            model = database.model(notion_id=item.id, **item.properties)

            try:
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
                    exist_dict = dict(orm)
                    exist_dict.pop("id")

                    update_dict = dict(exist)
                    update_dict.pop("id")

                    if update_dict != exist_dict:
                        await log_repo.add_log(
                            table_name=database.orm.__tablename__,
                            operation="MERGE",
                            row_id=exist.notion_id,
                            new_data=update_dict,
                            # TODO: add author
                        )
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
