import asyncio

from updater.src.notion.databases import DATABASE_REGISTRY, Directions, Persons
from updater.src.notion.poll_database import poll_database
from updater.src.states import UpdaterStates


class Updater:

    def __init__(self, notion):
        self.notion = notion
        self.states = UpdaterStates()

    async def run(self):
        if (
            not self.states.is_all_updater_running()
        ):  # check if not ran by telegram users
            self.states.start_all_updater()
            await asyncio.gather(
                *[
                    poll_database(self.notion, db())
                    for name, db in DATABASE_REGISTRY.items()
                ]
            )
            self.states.stop_all_updater()

    async def run_locations(self):
        self.states.start_location_updater()
        await poll_database(self.notion, Directions())
        self.states.stop_location_updater()

    async def run_persons(self):
        self.states.start_people_updater()
        await poll_database(self.notion, Persons())
        self.states.stop_people_updater()
