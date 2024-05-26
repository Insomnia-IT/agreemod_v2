import logging
from uuid import uuid4
from deepdiff import DeepDiff
import venusian
from sqlalchemy import select

from updater.src.states import UpdaterStates
from database.repo.logs import LogsRepository
from updater.src.config import config
from updater.src.notion.client import NotionClient
from updater.src.notion.databases import NotionDatabase

from database.meta import async_session
logger = logging.getLogger(__name__)

class NotionPoller:
    def __init__(self, db: NotionDatabase) -> None:
        self.set_status = {
            'get_people': UpdaterStates.set_people_updater,
            'get_directions': UpdaterStates.set_location_updater,
            'get_participation': self.dummy_state
        }
        self.database = db

    def dummy_state(self, state: bool):
        pass

    async def __aenter__(self):
        self.set_status[self.database.name](True)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.set_status[self.database.name](False)

    async def log_changes(self):
        pass

    async def poll_database(self, client: NotionClient):
        venusian.Scanner().scan(__import__("database"))
        response = await client.query_database(database=self.database, mock=False)
        logger.info(f"Received {self.database.name} table data")
        async with async_session() as session:
            log_repo = LogsRepository(session)
            for item in response:
                model = self.database.model(notion_id=item.id, **item.properties)
                exist = await session.scalar(
                    select(self.database.orm).filter_by(notion_id=orm.notion_id)
                )
                try:
                    orm = client.convert_model(model, self.database.orm)
                except Exception as e:

                    logger.error(f"{e.__class__.__name__}: {e}")
                    continue
                if not exist:
                    orm.id = uuid4()
                    session.add(orm)
                else:
                    orm.id = exist.id
                    if DeepDiff(dict(orm), dict(exist)):
                        await log_repo.add_log(
                            table_name=self.database.orm.__tablename__,
                            operation="MERGE",
                            row_id=exist.notion_id,
                            new_data=dict(orm),
                            # TODO: add author
                        )
                    await session.merge(orm)
            await session.commit()
            logger.info("Notion direction table data was stored to db")

if __name__ == "__main__":
    client = NotionClient(token=config.notion.token)
    # for name, db in DATABASE_REGISTRY.items():
    #     async with NotionPoller
    #     asyncio.run(poll_database(client, db()))
