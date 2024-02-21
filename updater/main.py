import asyncio

from updater.config import config, logger


async def main():
    notion = NotionDatabase(auth=config.notion.token)
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
