import logging

from notion_client import AsyncClient

from updater.notion.models.response import BaseNotionResponse, BaseNotionResponseItem


logger = logging.getLogger("NotionDatabase")


class NotionClient:
    def __init__(
        self,
        token: str,
    ):
        self._client = AsyncClient(auth=token)

    async def query_database(self, database, filters: dict = None) -> list[BaseNotionResponseItem]:
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
