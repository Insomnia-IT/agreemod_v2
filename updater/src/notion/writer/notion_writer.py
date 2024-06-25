import logging

from notion_client import Client
from updater.src.config import config
from updater.src.notion.client import NotionClient
import asyncio

logger = logging.getLogger(__name__)


class NotionWriter:

    def __init__(self):
        self.notion = NotionClient(token=config.notion.token_write)  # наш композитный объект с клиентом
        self.client: Client = self.notion._client  # оригинальный клиент

    async def retrieve_page(self, page_id):
        try:
            page = await self.client.pages.retrieve(page_id=page_id)
            return page
        except Exception as e:
            logger.error(f"Произошла ошибка при чтении страницы: {e}")
            return None

    async def update_page(self, page_id, properties):
        try:
            await self.client.pages.update(page_id=page_id, properties=properties)
            logger.info(f"Страница обновлена: {page_id}")
        except Exception as e:
            logger.error(f"Произошла ошибка при обновлении страницы: {e}")

    async def add_or_update_page(self, database_id, page_data, unique_id):
        try:
            page = await self.retrieve_page(unique_id)
            if page and unique_id:
                # Если запись существует, обновляем её
                await self.update_page(unique_id, page_data)
            else:
                # Если запись не существует, создаём новую
                response = await self.client.pages.create(parent={"database_id": database_id}, properties=page_data)
                logger.info(f"Новая запись создана: {response}")
        except Exception as e:
            logger.error(f"Произошла ошибка: {e}")


async def main():
    """
    Эта функция исключительно для разработки
    """
    notion_writer = NotionWriter()
    database_id = "56b5571508e046e8b0db41b3e448d557"  # Замените на ваш идентификатор базы данных
    unique_id = "08fe99b5c9344932a6c05a685d35c1c1"  # Уникальный идентификатор для записи

    # Данные для записи или обновления
    page_data = {
        "Имя": {
            "rich_text": [
                {
                    "text": {
                        "content": "Новое имя 88"
                    }
                }
            ]
        },
        "Фамилия": {
            "rich_text": [
                {
                    "text": {
                        "content": "Новая фамилия 88"
                    }
                }
            ]
        }
    }

    # Добавление или обновление страницы
    await notion_writer.add_or_update_page(database_id, page_data, unique_id)


if __name__ == '__main__':
    asyncio.run(main())
