"""
Скрипт для восстановления данных из coda в notion по заданному временному интервалу
момент когда были записанны не корректные данные

по времени когда был запущен скрипт
"""

import asyncio
import json
import logging
from datetime import datetime

import pandas as pd
import pytz

from database.meta import async_session
from database.repo.badges import BadgeRepo
from updater.src.notion.writer.construct_badge_data import construct_badge_data, \
    extract_and_construct_badge_data_from_notion
from app.notion.notion_writer import NotionWriter

logger = logging.getLogger(__name__)


async def notion_writer():
    file_path = "dev/badges.xlsx"
    df_coda_badge = pd.read_excel(file_path)

    notion_w = NotionWriter()
    database_id = "961e56d8f00e474bb3ab468c00eab53a"

    with open("dev/notion_badge_database_dump_27-06-24-15-14.json", "r") as file:
        badges = json.load(file)

    total = 0
    logger.info("start sync badges...")

    updated = []
    failed = []
    for badge in badges:
        cur_badge_id = badge.get("id")
        cur_badge_id_collapsed = str(cur_badge_id).replace("-", '')
        coda_doc = df_coda_badge.loc[df_coda_badge['page_id'] == cur_badge_id]
        if len(coda_doc) > 0:
            coda_doc = dict(coda_doc.iloc[0])
        else:
            continue

        time_str = badge.get('last_edited_time')

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
            try:
                print("Время попадает в заданный промежуток по Москве.")
                page_data = construct_badge_data(
                    title=coda_doc.get('Надпись'),
                    services_and_locations_id=coda_doc.get('directions'),
                    role_id=coda_doc.get('Role'),
                    position=coda_doc.get('Должность'),
                    last_name=coda_doc.get('Фамилия'),
                    first_name=coda_doc.get('Имя'),
                    gender=coda_doc.get('Пол'),
                    is_child=coda_doc.get('Ребенок'),
                    dietary_restrictions=coda_doc.get('Особенности питания'),
                    meal_type=coda_doc.get('Тип питания'),
                    party=str(coda_doc.get('Партия')) if coda_doc.get('Партия') is not None else None
                )
                await notion_w.add_or_update_page(database_id, page_data, cur_badge_id_collapsed)
                total += 1
                updated.append(cur_badge_id)
            except Exception as e:
                logger.error(e)
                failed.append(cur_badge_id)
        else:
            print("Время не попадает в заданный промежуток по Москве.")

    with open("updated.txt", 'w', encoding='utf-8') as file:
        json.dump(updated, file, ensure_ascii=False, indent=4)

    with open("failed.txt", 'w', encoding='utf-8') as file:
        json.dump(updated, file, ensure_ascii=False, indent=4)

    await asyncio.sleep(120)


if __name__ == '__main__':
    asyncio.run(notion_writer())
