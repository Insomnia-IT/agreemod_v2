import asyncio

from updater.src.config import config, logger
from updater.src.notion import NotionClient
from updater.src.updater import Updater


async def main():
    notion = NotionClient(token=config.notion.token)
    updater = Updater(notion=notion)

    while True:
        try:
            await updater.run()
        except Exception as e:
            logger.error(f"{e.__class__.__name__}: {e}")
        logger.info(f"Waiting for {config.REFRESH_PERIOD} seconds for the next update.")
        await asyncio.sleep(config.REFRESH_PERIOD)


def run_updater_async():
    asyncio.run(main())


if __name__ == "__main__":
    run_updater_async()
