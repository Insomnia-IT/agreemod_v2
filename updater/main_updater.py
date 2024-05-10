import asyncio

from updater.src.config import config, logger
from updater.src.notion import NotionClient
from updater.src.rabbit.manager import rmq_eat_carrots
from updater.src.updater import Updater


async def main(updater: Updater):
    while True:
        try:
            if not any(
                    [
                        updater.states.people_updating,
                        updater.states.location_updating,
                    ]
            ):
                await updater.run()
        except Exception as e:
            logger.error(f"{e.__class__.__name__}: {e}")
        logger.info(f"Waiting for {config.REFRESH_PERIOD} seconds for the next update.")
        await asyncio.sleep(config.REFRESH_PERIOD)


async def run_concurrently():
    # notion = NotionClient(token=config.notion.token_write)
    notion = NotionClient(token=config.notion.token)
    updater = Updater(notion=notion)

    await asyncio.gather(main(updater), rmq_eat_carrots(updater))
    # await updater.run_participation_db_to_notion()  # TODO: for dev
    # await updater.run_participation_notion_to_db()  # TODO: for dev


if __name__ == "__main__":
    asyncio.run(run_concurrently())
