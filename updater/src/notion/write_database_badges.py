"""
Рабочая промежуточная реализация синхронизация Бейджей в Notion
В текущей реализации создаются новые записи а не обновляются старые
"""

from notion_client import Client
from updater.src.config import config
from updater.src.notion.client import NotionClient

# Пример данных для добавления/обновления
page_data = {
    "Надпись": {
        "title": [
            {
                "text": {
                    "content": "Рюкзак"
                }
            }
        ]
    },
    "Службы и локации": {
        "relation": [
            {
                "id": "08fe99b5-c934-4932-a6c0-5a685d35c1c1"  # Заменить на актуальный
            }
        ]
    },
    "Роль": {
        "relation": [
            {
                "id": "9f8714fa-106d-4c67-84c7-5ea22b0b60b7"  # Заменить на актуальный ID
            }
        ]
    },
    "Должность": {
        "rich_text": [
            {
                "text": {
                    "content": "Артист Карнавала"
                }
            }
        ]
    },
    "Фамилия": {
        "rich_text": [
            {
                "text": {
                    "content": "ТЕСТ"
                }
            }
        ]
    },
    "Имя": {
        "rich_text": [
            {
                "text": {
                    "content": "ТЕСТ"
                }
            }
        ]
    },
    "Пол": {
        "select": {
            "name": "М"
        }
    },
    "Ребенок": {
        "checkbox": False
    },
    "Телефон": {
        "rich_text": [
            {
                "text": {
                    "content": "+79999999999"
                }
            }
        ]
    },
    "Особенности питания": {
        "select": {
            "name": "Без особенностей"
        }
    },
    "Тип питания": {
        "select": {
            "name": "Бесплатно"
        }
    },
    "Фото": {
        "files": [
            {
                "name": "avatar.jpg",
                "file": {
                    "url": "https://prod-files-secure.s3.us-west-2.amazonaws.com/f8e39894-4d91-4bbc-a2f0-2997b3523b3d/bd22e81c-99b9-44f6-b476-4d21d916b66c/11zon_cropped_%284%29.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240619%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240619T150004Z&X-Amz-Expires=3600&X-Amz-Signature=18002bd50abf49e32bc8bba23ef7db4959de7250a10dadfaf557d1eaead36d8d&X-Amz-SignedHeaders=host&x-id=GetObject"
                }
            }
        ]
    },
    "Партия": {
        "select": {
            "name": "4"
        }
    },
    "Цвет": {
        "select": {
            "name": "Оранжевый"
        }
    },
    "Комментарий": {
        "rich_text": [
            {
                "text": {
                    "content": ""
                }
            }
        ]
    }
}

# Локальная структура данных для хранения соответствий // в процессе
notion_id_map = {
    "unique_notion_id_123": "page_id_from_notion_1",
    # Другие соответствия
}


async def add_or_update_page(notion, database_id, page_data, unique_id):
    try:
        # Проверяем, существует ли запись с данным уникальным идентификатором
        if unique_id in notion_id_map:
            # Если запись существует, обновляем её
            page_id = notion_id_map[unique_id]
            await notion._client.pages.update(page_id=page_id, properties=page_data)
            print(f"Запись обновлена: {page_id}")
        else:
            # Если запись не существует, создаём новую
            response = await notion._client.pages.create(parent={"database_id": database_id}, properties=page_data)
            # Сохраняем новое соответствие
            notion_id_map[unique_id] = response['id']
            print("Новая запись создана")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == '__main__':
    import asyncio

    notion = NotionClient(token=config.notion.token_write)
    database_id = "56b5571508e046e8b0db41b3e448d557"  # Идентификатор базы данных
    unique_id = "08fe99b5-c934-4932-a6c0-5a685d35c1c1"  # Уникальный идентификатор

    asyncio.run(add_or_update_page(notion, database_id, page_data, unique_id))
