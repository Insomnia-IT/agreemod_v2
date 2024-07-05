"""
Скрипт для восстановления данных из coda в notion по заданному временному интервалу
момент когда были записанны не корректные данные

по 3 ошибочным полям
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


def is_russian_word(word):
    if word == 'Без питания':
        return True

    for char in word:
        if not ('А' <= char <= 'я' or char == 'ё' or char == 'Ё'):
            return False

    return True


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
    for badge in badges[-1317:-1017]:
        cur_badge_id = badge.get("id")
        cur_badge_id_collapsed = str(cur_badge_id).replace("-", '')
        coda_doc = df_coda_badge.loc[df_coda_badge['page_id'] == cur_badge_id]
        if len(coda_doc) > 0:
            coda_doc = dict(coda_doc.iloc[0])
        else:
            continue

        partiya_check = None
        food_lang = False
        not_rus_gender = False
        try:
            part_len = len(badge["properties"]["Партия"]["select"]["name"])
            partiya_check = part_len != 0 and part_len > 1
        except Exception:
            pass
        try:
            food = badge["properties"]["Тип питания"]["select"]["name"]
            food_lang = not is_russian_word(food)
        except Exception:
            pass

        try:
            name = badge["properties"]["Пол"]["select"]["name"]
            not_rus_gender = not is_russian_word(name)
        except Exception:
            pass

        # Проверка, попадает ли время в заданный промежуток
        if partiya_check or food_lang or not_rus_gender:
            try:
                print("Время попадает в заданный промежуток по Москве.")
                page_data = construct_badge_data(
                    # title=coda_doc.get('Надпись'),
                    services_and_locations_id=coda_doc.get('directions'),
                    # role_id=coda_doc.get('Role'),
                    # position=coda_doc.get('Должность'),
                    # last_name=coda_doc.get('Фамилия'),
                    # first_name=coda_doc.get('Имя'),
                    gender=coda_doc.get('Пол'),
                    # is_child=coda_doc.get('Ребенок'),
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
