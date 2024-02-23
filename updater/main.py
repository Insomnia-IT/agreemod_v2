import asyncio

from updater.config import config, logger
from updater.notion.client import NotionClient


class Updater:
    pass


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


if __name__ == "__main__":
    asyncio.run(main())
