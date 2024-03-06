import asyncio

from notion_client import Client as NotionDefaultClient

from updater.config import config, logger
from updater.notion.client import NotionClient
from updater.scripts.poll_notion_directions import poll_notion_directions


class Updater:

    def __init__(self, notion, notion_default_client):
        self.notion = notion
        self.notion_default_client = notion_default_client

    def run(self):
        poll_notion_directions(self.notion_default_client)


async def main():
    notion = NotionClient(token=config.notion.token)
    notion_default = NotionDefaultClient(auth=config.notion.token)
    updater = Updater(notion=notion, notion_default_client=notion_default)

    while True:
        try:
            updater.run()
        except Exception as e:
            logger.error(f"{e.__class__.__name__}: {e}")
        logger.info(f"Waiting for {config.REFRESH_PERIOD} seconds for the next update.")
        await asyncio.sleep(config.REFRESH_PERIOD)


if __name__ == "__main__":
    asyncio.run(main())
