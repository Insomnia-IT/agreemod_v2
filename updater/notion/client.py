import logging

from typing import Type

from notion_client import AsyncClient

from app.models.base import DomainModel
from updater.notion.databases import NotionDatabase
from updater.notion.models.base import BaseNotionResponse, BaseNotionResponseItem, NotionModel
from updater.notion.models.primitives.base import BaseNotionModel


logger = logging.getLogger("NotionDatabase")


class NotionClient:
    def __init__(
        self,
        token: str,
    ):
        self._client = AsyncClient(auth=token)

    async def query_database(self, database: NotionDatabase, filters: dict = None) -> list[BaseNotionResponseItem]:
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
        return complete_result

    @staticmethod
    def convert_model(notion: NotionModel, target: Type[DomainModel]) -> DomainModel:
        def calculate_value(value):
            if isinstance(value, BaseNotionModel):
                return value.value

            return value

        return target(**{key: calculate_value(val) for key, val in notion})
