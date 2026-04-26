import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database.repo.sync_states import SyncStateRepo
from database.orm.sync_state import SyncStateORM


logger = logging.getLogger(__name__)

SYNC_RESET_TIME = datetime(1970, 1, 1)


class SyncStateService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = SyncStateRepo(session)

    async def get_all(self) -> list[SyncStateORM]:
        return await self.repo.get_all()

    async def get_by_table(self, table_name: str) -> SyncStateORM | None:
        return await self.repo.get_by_table_name(table_name)

    async def reset_all(self) -> list[SyncStateORM]:
        states = await self.repo.get_all()
        for state in states:
            state.last_sync = SYNC_RESET_TIME
        await self.session.commit()
        logger.info("SyncState reset for all tables")
        return states

    async def reset_table(self, table_name: str) -> SyncStateORM | None:
        state = await self.repo.get_by_table_name(table_name)
        if not state:
            return None

        state.last_sync = SYNC_RESET_TIME
        await self.session.commit()

        logger.info(f"SyncState reset for table {table_name}")
        return state
