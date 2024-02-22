import logging

from updater.notion.models import BaseNotionResponse
from notion_client import AsyncClient


logger = logging.getLogger("NotionDatabase")


class NotionClient:
    def __init__(
        self,
        token: str,
    ):
        self._client = AsyncClient(auth=token)

    async def query_database(self, database, filters: dict = None) -> BaseNotionResponse:
        complete_result = []
        cursor = None
        while True:
            result = BaseNotionResponse(
                **await self._client.databases.query(
                    database_id=database.id,
                    filter=filters or database.filter,
                    start_cursor=cursor,
                )
            )
            # todo: обернуть вызов self.client.databases.query в проверку и бэкофф
            complete_result.extend(result.results)

            if result.has_more:
                cursor = result.next_cursor
                logger.info(f"{database.name}: Received {len(complete_result)} items")
            else:
                result.results = complete_result
                logger.info(f"{database.name}: Received {len(complete_result)} items total.")
                return result
