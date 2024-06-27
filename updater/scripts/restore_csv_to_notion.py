"""
Скрипт для восстановления данных из coda в notion по заданному временному интервалу
момент когда были записанны не корректные данные
"""

import asyncio
import logging
from datetime import datetime

import pandas as pd
import pytz

from database.meta import async_session
from database.repo.badges import BadgeRepo
from updater.src.notion.writer.construct_badge_data import construct_badge_data
from updater.src.notion.writer.notion_writer import NotionWriter

logger = logging.getLogger(__name__)


async def notion_writer():
    file_path = "dev/badges.xlsx"
    data = pd.read_excel(file_path)

    notion_w = NotionWriter()
    database_id = "56b5571508e046e8b0db41b3e448d557"

    total = 0
    async with (async_session() as session):
        logger.info("start sync badges...")
        repo = BadgeRepo(session)
        badges = await repo.get_all_badges()
        for badge in badges:
            badge_dict = dict(badge)
            cur_badge_id = badge_dict.get('notion_id')
            unique_id = str(cur_badge_id).replace("-", '')

            current_badge = await notion_w.retrieve_page(cur_badge_id)
            time_str = current_badge.get('last_edited_time')

            # Преобразование строки времени из формата UTC в объект datetime
            utc_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')

            # Установка временной зоны UTC для времени
            utc_time = utc_time.replace(tzinfo=pytz.UTC)

            # Перевод времени из UTC в московское время
            moscow_tz = pytz.timezone('Europe/Moscow')
            moscow_time = utc_time.astimezone(moscow_tz)

            # Определение промежутка времени по Москве
            start_time = moscow_tz.localize(datetime(moscow_time.year, moscow_time.month, moscow_time.day, 0, 20))
            end_time = moscow_tz.localize(datetime(moscow_time.year, moscow_time.month, moscow_time.day, 0, 45))

            # Проверка, попадает ли время в заданный промежуток
            if start_time <= moscow_time <= end_time:
                print("Время попадает в заданный промежуток по Москве.")
                total += 1
            else:
                print("Время не попадает в заданный промежуток по Москве.")

            page_data = None
            page_data = construct_badge_data(
                title=badge['name'],
                services_and_locations_id=str(badge['notion_id']),
                role_id=badge['role_code'],
                position=badge['occupation'],
                last_name=badge['last_name'],
                first_name=badge['first_name'],
                gender=badge['gender'],
                is_child=badge['infant_id'] is not None,
                phone=badge['phone'],
                dietary_restrictions=badge['diet'],
                meal_type=badge['feed'],
                photo_url=badge['photo'],
                photo_name=badge['nickname'],
                party=badge['number'],
                color=None,  # Заменить на подходящее значение, если оно есть
                comment=badge['comment']
            )

            if unique_id:
                unique_id = str(unique_id).replace("-", '')
                # Добавление или обновление страницы
                await notion_w.add_or_update_page(database_id, page_data, unique_id)
    print(total)
    await asyncio.sleep(120)


if __name__ == '__main__':
    asyncio.run(notion_writer())
