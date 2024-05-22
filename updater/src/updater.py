import asyncio

from updater.src.notion.databases import DATABASE_REGISTRY, Directions, NotionDatabase, Persons
from updater.src.notion.poll_database import NotionPoller
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

    async def run_locations(self, user_id, bot):
        async with NotionPoller(Directions()) as poll:
            await poll.poll_database(self.notion)
        await bot.send_message(user_id, "Обновление таблицы Направлений завершено")

    async def run_persons(self, user_id, bot):
        async with NotionPoller(Persons()) as poll:
            await poll.poll_database(self.notion)
        await bot.send_message(user_id, "Обновление таблицы Человеков завершено")
