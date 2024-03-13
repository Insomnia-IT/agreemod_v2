import logging
import os.path
import pickle

from typing import Type
from uuid import UUID

from notion_client import AsyncClient
from sqlalchemy.orm.decl_api import DeclarativeMeta
from updater.notion.databases import NotionDatabase
from updater.notion.models.base import (
    BaseNotionResponse,
    BaseNotionResponseItem,
    NotionModel,
)
from updater.notion.models.primitives.base import BaseNotionModel


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
            if database.id == "c565f5fca2df40628cd91cfd59da4a9d":  # TODO: get from enum
                response = self.load_mocked_persons()
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

        if mock:
            logger.info("creating mock files...")
            # TODO: probably this should be done with decorator
            if database.id == "c565f5fca2df40628cd91cfd59da4a9d":
                self.save_persons_mock(complete_result)

        return complete_result

    @staticmethod
    def convert_model(
        notion: NotionModel, target: Type[DeclarativeMeta]
    ) -> DeclarativeMeta:
        def calculate_value(value):
            if isinstance(value, BaseNotionModel):
                return value.value
            elif isinstance(value, UUID):
                return value.hex

            return value

        return target(
            **{key: calculate_value(val) for key, val in notion if key[-1] != "_"}
        )

    @staticmethod
    def load_mocked_persons():
        mock_path = os.path.join("mocks", "notion_response_persons.pickle")
        if os.path.exists(mock_path):
            with open(mock_path, "rb") as f:
                return pickle.load(f)
        else:
            return None

    @staticmethod
    def save_persons_mock(data):
        mock_path = os.path.join("mocks", "notion_response_persons.pickle")
        with open(mock_path, "wb") as f:
            pickle.dump(data, f)
