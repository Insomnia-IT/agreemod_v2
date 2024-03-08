import asyncio

from updater.config import config, logger
from updater.notion.client import NotionClient
from updater.scripts.poll_notion_directions import poll_notion_directions


class Updater:

    def __init__(self, notion):
        self.notion = notion

    async def run(self):
        await poll_notion_directions(self.notion)


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
