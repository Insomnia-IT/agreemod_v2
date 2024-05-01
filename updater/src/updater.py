import asyncio

from updater.src.notion.write_database import write_database
from updater.src.notion.databases import DATABASE_REGISTRY, Directions, Persons, Participations
from updater.src.notion.poll_database import poll_database
from updater.src.states import UpdaterStates


class Updater:

    def __init__(self, notion):
        self.notion = notion
        self.states = UpdaterStates()

    async def run(self):
        if not self.states.all_updating:  # check if not ran by telegram users
            self.states.start_all_updater()
            await asyncio.gather(
                *[
                    poll_database(self.notion, db())
                    for name, db in DATABASE_REGISTRY.items()
                ]
            )
            self.states.stop_all_updater()

    async def run_locations(self, user_id, bot):
        """Notion to DB
        """
        self.states.start_location_updater()
        await poll_database(self.notion, Directions())
        self.states.stop_location_updater()
        await bot.send_message(user_id, "Обновление таблицы Направлений завершено")

    async def run_persons(self, user_id=None, bot=None):
        """Notion to DB
        """
        self.states.start_people_updater()
        await poll_database(self.notion, Persons())
        self.states.stop_people_updater()
        if user_id and bot:
            await bot.send_message(user_id, "Обновление таблицы Человеков завершено")

    async def run_participation(self, user_id=None, bot=None):
        """Notion to DB
        """
        self.states.start_participation_updater()
        await poll_database(self.notion, Participations())
        self.states.stop_participation_updater()
        if user_id and bot:
            await bot.send_message(user_id, "Обновление таблицы Человеков завершено")

    async def run_participation_to_notion(self):
        """DB to Notion
        """
        await write_database(self.notion)
