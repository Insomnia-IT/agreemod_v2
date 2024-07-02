import asyncio

from database.meta import async_session
from database.repo.badges import BadgeRepo
from updater.src.coda.client import CodaClient
from updater.src.config import config, logger
from updater.src.notion.client import NotionClient
from updater.src.notion.databases import CODA_DB_REGISTRY, NOTION_DB_REGISTRY, dbs
from updater.src.notion.poll_database import CodaPoller, NotionPoller
from updater.src.notion.writer.construct_badge_data import construct_badge_data
from updater.src.notion.writer.notion_writer import NotionWriter
from updater.src.rabbit.manager import rmq_eat_carrots
from updater.src.updater import Updater


async def main(notion: NotionClient, coda: CodaClient):
    while True:
        notion_updater = Updater(notion, NotionPoller, NOTION_DB_REGISTRY)
        coda_updater = Updater(coda, CodaPoller, CODA_DB_REGISTRY)
        try:
            if not any(
                    [
                        notion_updater.states.people_updating,
                        notion_updater.states.location_updating,
                    ]
            ):
                await notion_updater.run()
        except Exception as e:
            logger.error(f"{e.__class__.__name__}: {e}")
        try:
            if not any(
                    [
                        coda_updater.states.participation_updating,
                        coda_updater.states.arrival_updating,
                    ]
            ):
                await coda_updater.run()
        except Exception as e:
            logger.error(f"{e.__class__.__name__}: {e}")
        logger.info(f"Waiting for {config.REFRESH_PERIOD} seconds for the next update.")
        await asyncio.sleep(config.REFRESH_PERIOD)


async def notion_writer():
    notion_w = NotionWriter()
    database_id = dbs["get_badges"]["id"]

    async with (async_session() as session):
        logger.info("start sync badges...")
        repo = BadgeRepo(session)
        badges = await repo.get_all_badges()
        for badge in badges:
            badge = dict(badge)
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
                dietary_restrictions=badge['diet'],
                meal_type=badge['feed'],
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
    logger.info("finished sync badges... sleep...")
    await asyncio.sleep(config.REFRESH_PERIOD)


async def run_concurrently():
    notion = NotionClient(token=config.notion.token)
    if config.TESTING:
        coda = CodaClient(api_key=config.coda.api_key, doc_id='qvssosHV4b')
    else:
        coda = CodaClient(api_key=config.coda.api_key, doc_id=config.coda.doc_id)

    await asyncio.gather(
        main(notion=notion, coda=coda),
        # notion_writer(),
        # rmq_eat_carrots())
    )


if __name__ == "__main__":
    asyncio.run(run_concurrently())
    # asyncio.run(notion_writer())
