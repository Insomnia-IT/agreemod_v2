import logging
import os.path
import pickle
from typing import Type, Union
from uuid import UUID

from notion_client import AsyncClient
from sqlalchemy.orm.decl_api import DeclarativeMeta

from database.orm.participation import ParticipationORM
from updater.src.notion.databases import (
    Directions,
    NotionDatabase,
    Participations,
    Persons,
)
from updater.src.notion.models.base import BaseNotionResponse, BaseNotionResponseItem
from updater.src.notion.models.primitives.base import BaseNotionModel

logger = logging.getLogger("NotionDatabase")


class NotionClient:
    def __init__(
        self,
        token: str,
    ):
        self._client = AsyncClient(auth=token)

    async def query_database(
        self, database: NotionDatabase, filters: dict = None, mock=False
    ) -> list[BaseNotionResponseItem]:
        """
        Метод читает данные из таблиц Notion.
        database:
        filters:
        mock: Параметр позволяет читать даные из сохранённых обьектов pickle (удобно для разработки).
        Если обьект не найден, програма прочитает данные из notion и создат файл pickle.
        """

        if mock is True:
            logger.info("try reading mock files...")
            response = self.load_mocked(database.name)
            if response:
                return response

        complete_result = []
        result = BaseNotionResponse(
            **await self._client.databases.query(
                database_id=database.id,
                start_cursor=None,
            )
        )
        complete_result.extend(result.results)
        self.save_mock(database.name, complete_result)

        logger.info(f"{database.name}: Received {len(complete_result)} items")
        while result.has_more:
            # todo: обернуть вызов self.client.databases.query в проверку и бэкофф
            cursor = result.next_cursor
            result = BaseNotionResponse(
                **await self._client.databases.query(
                    database_id=database.id,
                    start_cursor=cursor,
                )
            )
            complete_result.extend(result.results)
            logger.info(f"{database.name}: Received {len(complete_result)} items")
        logger.info(f"{database.name}: Received {len(complete_result)} items total.")

        return complete_result

    @staticmethod
    def convert_model(
        notion: Union[
            Directions,
            Persons,
            Participations,
        ],
        target: Type[DeclarativeMeta],
    ) -> DeclarativeMeta:
        def calculate_value(value):
            if isinstance(value, BaseNotionModel):
                return value.value
            elif isinstance(value, UUID):
                return value.hex

            return value

        orm = target(
            **{key: calculate_value(val) for key, val in notion if key[-1] != "_"}
        )

        if type(orm) is ParticipationORM:
            # TODO: убрать этот костыль
            if not orm.person_id:
                raise Exception("No user id provided")
            orm.direction_id = str(orm.direction_id[0].hex)
            orm.person_id = str(orm.person_id[0].hex)

        return orm

    @staticmethod
    def load_mocked(db_name: str):
        if db_name not in ["get_people", "get_participation"]:
            logger.warning(f"{db_name} not added to pickle loader")
            return None

        os.makedirs("mocks", exist_ok=True)
        mock_path = os.path.join("mocks", f"{db_name}.pickle")
        if os.path.exists(mock_path):
            with open(mock_path, "rb") as f:
                return pickle.load(f)
        else:
            return None

    @staticmethod
    def save_mock(file_name: str, data):
        logger.info("creating mock files...")
        os.makedirs("mocks", exist_ok=True)
        mock_path = os.path.join("mocks", f"{file_name}.pickle")
        with open(mock_path, "wb") as f:
            pickle.dump(data, f)
