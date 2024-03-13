import asyncio

from updater.config import config, logger
from updater.notion.client import NotionClient
from updater.notion.databases import DATABASE_REGISTRY
from updater.notion.poll_database import poll_database


class Updater:

    def __init__(self, notion):
        self.notion = notion

    async def run(self):
        await asyncio.gather(
            *[
                poll_database(self.notion, db())
                for name, db in DATABASE_REGISTRY.items()
            ]
        )


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
