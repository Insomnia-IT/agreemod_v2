import asyncio

from updater.src.coda.client import CodaClient
from updater.src.config import config, logger
from updater.src.notion.client import NotionClient
from updater.src.notion.databases import CODA_DB_REGISTRY, NOTION_DB_REGISTRY
from updater.src.notion.poll_database import CodaPoller, NotionPoller
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


async def run_concurrently():
    # notion = NotionClient(token=config.notion.token_write)
    notion = NotionClient(token=config.notion.token)
    coda = CodaClient(api_key=config.coda.api_key, doc_id=config.coda.doc_id)

    await asyncio.gather(
        main(notion=notion, coda=coda),  # rmq_eat_carrots())
    )


if __name__ == "__main__":
    asyncio.run(run_concurrently())
