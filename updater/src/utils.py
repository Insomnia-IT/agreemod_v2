from uuid import UUID

from notion_client import Client
from updater.src.config import config
from updater.src.notion.models.base import NotionModel
from updater.src.notion.models.primitives.base import BaseNotionModel


def query_notion_database(database: str, full: bool = False) -> list[dict]:
    """
    Метод читает данные из таблиц Notion.
    database:
    """
    client = Client(auth=config.notion.token)
    complete_result = []
    with client as c:
        result = c.databases.query(database_id=database)
        complete_result.extend(result["results"])
        while result["has_more"]:
            cursor = result["next_cursor"]
            result = c.databases.query(
                database_id=database,
                start_cursor=cursor,
            )
            complete_result.extend(result["results"])
    if full:
        return complete_result
    properties = []
    for r in complete_result:
        r["properties"].update({"notion_id": r["id"]})
        properties.append(r["properties"])
    return properties


def convert_model(notion: NotionModel) -> dict:
    def calculate_value(value):
        if isinstance(value, BaseNotionModel):
            return value.value
        elif isinstance(value, UUID):
            return value
        return value

    return {key: calculate_value(val) for key, val in notion if key[-1] != "_"}
