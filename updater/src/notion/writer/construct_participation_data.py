from typing import Dict, Optional
from updater.src.config import config
from updater.src.notion.client import NotionClient


def construct_participation_data(
        person_id: Optional[str] = None,
        year: Optional[str] = None,
        services_and_locations_id: Optional[str] = None,
        role: Optional[str] = None,
        type_: Optional[str] = None,  # Используем type_ вместо type, чтобы избежать конфликта с ключевым словом Python
        status: Optional[str] = None
) -> Dict[str, Dict]:
    data = {}

    if person_id:
        data["Человек"] = {
            "relation": [
                {
                    "id": person_id
                }
            ]
        }

    if year:
        data["Год"] = {
            "rich_text": [
                {
                    "text": {
                        "content": year
                    }
                }
            ]
        }

    if services_and_locations_id:
        data["Службы и локации"] = {
            "relation": [
                {
                    "id": services_and_locations_id
                }
            ]
        }

    if role:
        data["Роль"] = {
            "select": {
                "name": role
            }
        }

    if type_:
        data["Тип"] = {
            "select": {
                "name": type_
            }
        }

    if status:
        data["Статус"] = {
            "select": {
                "name": status
            }
        }

    return data


if __name__ == '__main__':
    # Пример использования функции-конструктора
    new_page_data = construct_participation_data(
        person_id="bd94bff7-4bd3-4a71-b3c0-d8a5a571a3df",
        year="4027",
        services_and_locations_id="b30c7137-a840-45d2-85e0-033d9b5d8d44",
        role="Волонтёр",
        type_="Городская служба",
        status="Активен"
    )

    print(new_page_data)

    import asyncio

    notion = NotionClient(token=config.notion.token_write)
    database_id = "9f19e90d8ef74620b5c005ddf0dea4e4"
    asyncio.run(notion._client.pages.create(parent={"database_id": database_id}, properties=new_page_data))
