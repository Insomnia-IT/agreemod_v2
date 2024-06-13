import logging

from abc import ABC, abstractmethod
from datetime import date, datetime, time
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

import asyncpg
import venusian

from database.meta import async_session
from database.orm.badge import AnonsORM, BadgeORM
from database.orm.badge_directions import BadgeDirectionsORM
from database.repo.logs import LogsRepository
from deepdiff import DeepDiff
from pydantic import BaseModel, ValidationError
from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from updater.src.coda.client import CodaClient
from updater.src.config import config
from updater.src.notion.client import NotionClient
from updater.src.notion.databases import CodaDatabase, NotionDatabase
from updater.src.states import UpdaterStates


logger = logging.getLogger(__name__)


def mk_diff_serializable(diff: dict):
    for change_type, fields in diff.items():
        for field, changes in fields.items():
            for old_new, value in changes.items():
                diff[change_type][field][old_new] = str(value)
    return diff


def adapt_value(value: Any):
    if isinstance(value, asyncpg.pgproto.pgproto.UUID):
        return UUID(str(value))
    elif isinstance(value, Enum):
        return value.value
    elif isinstance(value, (datetime, date, time)):
        return value.isoformat()
    else:
        return value


def adapt_to_serialize(value: Any):
    if isinstance(value, (asyncpg.pgproto.pgproto.UUID, UUID)):
        return str(value)
    elif isinstance(value, Enum):
        return value.value
    elif isinstance(value, (datetime, date, time)):
        return value.isoformat()
    else:
        return value


class Poller(ABC):
    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        pass

    @abstractmethod
    async def poll_database(self, client):
        pass


class NotionPoller(Poller):
    def __init__(self, db: NotionDatabase) -> None:
        self.set_status = {
            "get_people": UpdaterStates.set_people_updater,
            "get_directions": UpdaterStates.set_location_updater,
            "get_badges": UpdaterStates.set_badge_updater,
            "anonymous_badges": self.set_dummy,
        }
        self.database = db

    def set_dummy(self, a: bool):
        return

    async def __aenter__(self):
        self.set_status[self.database.name](True)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.set_status[self.database.name](False)

    async def log_changes(self):
        pass

    async def poll_database(self, client: NotionClient):
        venusian.Scanner().scan(__import__("database"))
        response = await client.query_database(database=self.database, mock=False)
        logger.info(f"Received {self.database.name} table data")
        chunk = 50 if self.database.name != "get_badges" else 1
        for items in [response[x : x + chunk] for x in range(0, len(response), chunk)]:
            try:
                async with async_session() as session:
                    log_repo = LogsRepository(session)
                    for item in items:
                        try:
                            model = self.database.model(
                                notion_id=item.id, **item.properties
                            )
                        except ValidationError as e:
                            logger.error(
                                f"{self.database.name} model validation error: {e.errors()}"
                            )
                            continue
                        exist = await session.scalar(
                            select(self.database.orm).filter_by(
                                notion_id=model.notion_id
                            )
                        )
                        try:
                            orm = client.convert_model(model, self.database.orm)
                        except Exception as e:

                            logger.error(f"{e.__class__.__name__}: {e}")
                            continue
                        if not exist:
                            if not isinstance(orm, AnonsORM):
                                orm.id = uuid4()
                            session.add(orm)
                        else:
                            if isinstance(orm, AnonsORM):
                                orm.notion_id = exist.notion_id
                            else:
                                orm.id = exist.id
                            diff = DeepDiff(
                                {
                                    x: adapt_value(y)
                                    for x, y in dict(exist).items()
                                    if x not in ["last_updated", "photo"]
                                },
                                {
                                    x: adapt_value(y)
                                    for x, y in dict(orm).items()
                                    if x not in ["last_updated", "photo"]
                                },
                            )
                            # update photo for badges but not change last_updated if photo is the only difference
                            if isinstance(orm, BadgeORM):
                                photo_diff = exist.photo == orm.photo
                                if not diff and photo_diff:
                                    orm.last_updated = exist.last_updated
                                    await session.merge(orm)
                            if diff:
                                await log_repo.add_log(
                                    table_name=self.database.orm.__tablename__,
                                    operation="MERGE",
                                    row_id=exist.id,
                                    new_data={
                                        x: adapt_to_serialize(y)
                                        for x, y in dict(orm).items()
                                    },
                                    author="Notion",
                                )
                                await session.merge(orm)
                        if isinstance(orm, BadgeORM):
                            for direction in model.direction_id_.value:
                                badge_dir_exist = await session.scalar(
                                    select(BadgeDirectionsORM).where(
                                        and_(
                                            BadgeDirectionsORM.badge_id == orm.id,
                                            BadgeDirectionsORM.direction_id
                                            == direction,
                                        )
                                    )
                                )
                                if not badge_dir_exist:
                                    session.add(
                                        BadgeDirectionsORM(
                                            badge_id=orm.id, direction_id=direction
                                        )
                                    )
                    await session.commit()
            except IntegrityError as e:
                logger.error(e)
                continue
            logger.info(
                f"{self.database.name} table {len(items)} rows were stored to db"
            )


class CodaPoller(Poller):
    def __init__(self, db: CodaDatabase) -> None:
        self.set_status = {
            "get_participations": UpdaterStates.set_participation_updater,
            "get_arrivals": UpdaterStates.set_arrival_updater,
        }
        self.database = db

    async def __aenter__(self):
        self.set_status[self.database.name](True)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.set_status[self.database.name](False)

    async def poll_database(self, coda: CodaClient):
        venusian.Scanner().scan(__import__("database"))
        data = coda.get_table(self.database.id)
        logger.info(f"Received {self.database.name} table data")
        chunk = 50
        for items in [data[x : x + chunk] for x in range(0, len(data), chunk)]:
            try:
                async with async_session() as session:
                    log_repo = LogsRepository(session)
                    for item in items:
                        try:
                            model: BaseModel = self.database.model(**item)
                        except ValidationError as e:
                            if not next(
                                (
                                    x
                                    for x in e.errors()
                                    if x["type"] == "assertion_error"
                                    and ("Год" in x["loc"] or "Дата заезда" in x["loc"])
                                ),
                                None,
                            ):
                                logger.error(
                                    f"{self.database.name} model validation error: {e.errors()}"
                                )
                                logger.error(str(item))
                            continue
                        exist = await session.scalar(
                            select(self.database.orm).filter_by(
                                coda_index=model.coda_index
                            )
                        )
                        try:
                            orm = self.database.orm(**model.model_dump())
                        except Exception as e:
                            logger.error(f"{e.__class__.__name__}: {e}")
                            continue
                        if not exist:
                            orm.id = uuid4()
                            session.add(orm)
                        else:
                            orm.id = exist.id
                            diff = DeepDiff(
                                {
                                    x: adapt_value(y)
                                    for x, y in dict(exist).items()
                                    if x != "last_updated"
                                },
                                {
                                    x: adapt_value(y)
                                    for x, y in dict(orm).items()
                                    if x != "last_updated"
                                },
                            )
                            if diff:
                                diff = mk_diff_serializable(diff)
                                await log_repo.add_log(
                                    table_name=self.database.orm.__tablename__,
                                    operation="MERGE",
                                    row_id=exist.id,
                                    new_data={
                                        x: adapt_to_serialize(y)
                                        for x, y in dict(orm).items()
                                    },
                                    author="Coda",
                                )
                                await session.merge(orm)
                    await session.commit()
            except IntegrityError as e:
                logger.error(e)
                continue
            logger.info(
                f"{self.database.name} table {len(items)} rows were stored to db"
            )


if __name__ == "__main__":
    client = NotionClient(token=config.notion.token)
    # for name, db in DATABASE_REGISTRY.items():
    #     async with NotionPoller
    #     asyncio.run(poll_database(client, db()))
