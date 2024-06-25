"""
Рабочая промежуточная реализация синхронизация Направлений в Notion
"""

from notion_client import Client

from updater.src.config import config
from updater.src.notion.client import NotionClient

# Пример данных для добавления
new_page_data = {
    "Человек": {
        "relation": [
            {
                "id": "bd94bff7-4bd3-4a71-b3c0-d8a5a571a3df"
            }
        ]
    },
    "Год": {
        "rich_text": [
            {
                "text": {
                    "content": "4027"
                }
            }
        ]
    },
    "Службы и локации": {
        "relation": [
            {
                "id": "b30c7137-a840-45d2-85e0-033d9b5d8d44"
            }
        ]
    },
    "Роль": {
        "select": {
            "name": "Волонтёр"
        }
    },
    "Тип": {
        "select": {
            "name": "Городская служба"
        }
    },
    "Статус": {
        "select": {
            "name": "Активен"
        }
    }
}

if __name__ == '__main__':
    import asyncio

    notion = NotionClient(token=config.notion.token_write)
    database_id = "9f19e90d8ef74620b5c005ddf0dea4e4"
    asyncio.run(notion._client.pages.create(parent={"database_id": database_id}, properties=new_page_data))
