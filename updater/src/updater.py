import asyncio

from updater.src.notion.poll_database import NotionPoller
from updater.src.notion.write_database import write_database
from updater.src.notion.databases import DATABASE_REGISTRY, Directions, Persons, Participations, NotionDatabase
from updater.src.states import UpdaterStates


class Updater:

    def __init__(self, notion):
        self.notion = notion
        self.states = UpdaterStates()

    async def run(self):
        async def run_single_db(db: NotionDatabase):
            async with NotionPoller(db()) as poll:
                await poll.poll_database(self.notion)
        
        await asyncio.gather(
            *[
                run_single_db(db)
                for name, db in DATABASE_REGISTRY.items()
            ]
        )

    async def run_locations(self, user_id=None, bot=None):
        async with NotionPoller(Directions()) as poll:
            await poll.poll_database(self.notion)
        if user_id and bot:
            await bot.send_message(user_id, "Обновление таблицы Направлений завершено")

    async def run_persons(self, user_id=None, bot=None):
        async with NotionPoller(Persons()) as poll:
            await poll.poll_database(self.notion)
        if user_id and bot:
            await bot.send_message(user_id, "Обновление таблицы Человеков завершено")

    async def run_participation_notion_to_db(self, user_id=None, bot=None):
        """Notion to DB
        Эту синхронизацию не нужно было делать.
        Её не нужно включать в основной поток синхронизации.
        """
        async with NotionPoller(Participations()) as poll:
            await poll.poll_database(self.notion, )
        self.states.stop_participation_updater()
        if user_id and bot:
            await bot.send_message(user_id, "Обновление таблицы Участия завершено")

    async def run_participation_db_to_notion(self, user_id=None, bot=None):
        """DB to Notion
        """
        self.states.start_participation_updater()
        # get db data
        await write_database(self.notion, "Participations")
        self.states.stop_participation_updater()
        if user_id and bot:
            await bot.send_message(user_id, "Обновление таблицы Участия завершено")
