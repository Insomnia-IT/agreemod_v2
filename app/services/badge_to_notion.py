import logging
from typing import Optional, Dict

import yaml
from notion_client import Client

from app.config import config
from database.meta import async_session
from database.repo.badges import BadgeRepo

logger = logging.getLogger(__name__)

with open("app/notion_db.yml", 'r', encoding='utf-8') as file:
    dbs = yaml.safe_load(file)

badge_data = {  # TODO: читать это из базы?! Или из ParticipationRole?
    "Волонтёр": "0459773f-44c7-48ca-b93a-3e34d6734af5",
    "Аниматор": "057f0f30-0918-445b-aa16-0f1c1c54e216",
    "Медик": "35d3f838-3b6d-47aa-8fe8-9f42c7e5cf5d",
    "Пресса": "45dd1e26-1b0e-45df-b451-472a240a2bb0",
    "Лектор": "48d62cd1-097a-4770-b36f-e6d77165675b",
    "Свои (плюсодины)": "5899450b-338d-4f6a-a1f9-1fa9fa7fc151",
    "VIP": "7f6da8d7-9b21-4e5d-ac0a-d545fff1a195",
    "Артист": "949fb54d-e39b-40e4-a452-2b5bb8874989",
    "Подрядчик": "98d86463-eb8e-4a64-8662-f609f69878be",
    "Мастер": "a381b28f-ad2a-4656-b434-4ad1bf9f6229",
    "Лидер нефедеральной локации": "aed0b237-0f3d-4974-9c73-e7d6a95a47dd",
    "Волонтёр нефедеральной локации": "ee79040c-8080-47e0-8f5a-1e4c423994a5",
    "Сопровождающие (участников)": "ffbe65c1-03f6-40b4-878b-c706fbb3aabf",
    "Бригадир": "9f8714fa-106d-4c67-84c7-5ea22b0b60b7",
    "Организатор": "31361def-f99f-4189-a347-86ecb75476f9",
    "Зам. руководителя": "48414ef4-776b-44ea-af5e-ad19c4fd1e42"
}


class NotionWriter:

    def __init__(self):
        self.client: Client = Client(auth=config.notion.write_token)

    def retrieve_page(self, page_id):
        try:
            page = self.client.pages.retrieve(page_id=page_id)
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
            page = self.retrieve_page(unique_id)
            if page and unique_id:
                # Если запись существует, обновляем её
                await self.update_page(unique_id, page_data)
            else:
                # Если запись не существует, создаём новую
                response = self.client.pages.create(parent={"database_id": database_id}, properties=page_data)
                logger.info(f"Новая запись создана: {response}")
        except Exception as e:
            logger.error(f"Произошла ошибка: {e}")


def construct_badge_data(
        title: Optional[str] = None,
        services_and_locations_id: Optional[str] = None,
        role_id: Optional[str] = None,
        position: Optional[str] = None,
        last_name: Optional[str] = None,
        first_name: Optional[str] = None,
        gender: Optional[str] = None,
        is_child: Optional[bool] = None,
        phone: Optional[str] = None,
        dietary_restrictions: Optional[str] = None,
        meal_type: Optional[str] = None,
        photo_url: Optional[str] = None,
        photo_name: Optional[str] = None,
        party: Optional[str] = None,
        color: Optional[str] = None,
        comment: Optional[str] = None
) -> Dict[str, Dict]:
    data = {}

    if title:
        data["Надпись"] = {
            "title": [
                {
                    "text": {
                        "content": title
                    }
                }
            ]
        }

    if services_and_locations_id:
        data["Службы и локации"] = {
            "relation": [{"id": i} for i in services_and_locations_id.split(",")]
        }

    if role_id:
        role_name = badge_data.get(role_id)
        if role_name:
            data["Роль"] = {
                "relation": [
                    {
                        # "id": ParticipationRole[role_id].value
                        "id": role_name  # TODO: читать из enum
                    }
                ]
            }

    if position and str(position) != 'nan':
        data["Должность"] = {
            "rich_text": [
                {
                    "text": {
                        "content": position
                    }
                }
            ]
        }

    if last_name and str(last_name) != 'nan':
        data["Фамилия"] = {
            "rich_text": [
                {
                    "text": {
                        "content": last_name
                    }
                }
            ]
        }

    if first_name and str(first_name) != 'nan':
        data["Имя"] = {
            "rich_text": [
                {
                    "text": {
                        "content": first_name
                    }
                }
            ]
        }

    if gender and str(gender) != 'nan':
        data["Пол"] = {
            "select": {
                "name": gender
            }
        }

    if bool(is_child):
        data["Ребенок"] = {
            "checkbox": bool(is_child)
        }

    if phone and str(phone) != 'nan':
        data["Телефон"] = {
            "rich_text": [
                {
                    "text": {
                        "content": phone
                    }
                }
            ]
        }

    if dietary_restrictions and str(dietary_restrictions) != 'nan':
        data["Особенности питания"] = {
            "select": {
                "name": dietary_restrictions
            }
        }

    if meal_type and str(meal_type) != 'nan':
        data["Тип питания"] = {
            "select": {
                "name": meal_type
            }
        }

    if photo_url and photo_name:
        data["Фото"] = {
            "files": [
                {
                    "name": photo_name,
                    "file": {
                        "url": photo_url
                    }
                }
            ]
        }

    if party and str(party) != 'nan':
        data["Партия"] = {
            "select": {
                "name": str(int(float(party)))
            }
        }

    if color and str(color) != 'nan':
        data["Цвет"] = {
            "select": {
                "name": color
            }
        }

    if comment and str(comment) != 'nan':
        data["Комментарий"] = {
            "rich_text": [
                {
                    "text": {
                        "content": comment
                    }
                }
            ]
        }

    return data


async def notion_writer():
    notion_w = NotionWriter()
    database_id = dbs["get_badges"]["id"]

    async with (async_session() as session):
        logger.info("start sync badges...")
        repo = BadgeRepo(session)
        badges = await repo.get_all_badges()
        for badge in badges:
            try:
                badge = dict(badge)

                diet = "Без особенностей" if badge['diet'] == 'STANDARD' else "Веган" if badge[
                                                                                             'diet'] == 'VEGAN' else "Unknown"
                feed = "Бесплатно" if badge['feed'] == 'FREE' else "Платно" if badge[
                                                                                   'diet'] == 'PAID' else "Без питания"
                page_data = construct_badge_data(
                    title=badge['name'],
                    services_and_locations_id=str(badge['notion_id']),
                    role_id=badge['role_code'],
                    position=badge['occupation'],
                    last_name=badge['last_name'],
                    first_name=badge['first_name'],
                    gender="Ж" if badge['gender'] == 'FEMALE' else "M" if badge['gender'] == 'MALE' else "Unknown",
                    is_child=badge['infant_id'] is not None,
                    phone=badge['phone'],
                    dietary_restrictions=diet,
                    meal_type=feed,
                    # photo_url=badge['photo'],
                    photo_name=badge['nickname'],
                    party=badge.get("batch"),
                    color=None,  # Заменить на подходящее значение, если оно есть
                    comment=badge['comment']
                )

                unique_id = badge.get('notion_id')
                if unique_id:
                    unique_id = str(unique_id).replace("-", '')
                    # Добавление или обновление страницы
                    await notion_w.add_or_update_page(database_id, page_data, unique_id)
            except Exception as e:
                logger.error(e)

    logger.info("finished sync badges... sleep...")
