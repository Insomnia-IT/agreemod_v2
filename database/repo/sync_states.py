from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.orm.sync_state import SyncStateORM


class SyncStateRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_table_name(self, table_name: str) -> Optional[SyncStateORM]:
        query = select(SyncStateORM).where(SyncStateORM.table_name == table_name)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_all(self) -> list[SyncStateORM]:
        result = await self.session.execute(select(SyncStateORM))
        return result.scalars().all()

    async def upsert(self, table_name: str, last_sync: datetime) -> SyncStateORM:
        obj = await self.get_by_table_name(table_name)

        if obj:
            obj.last_sync = last_sync
        else:
            obj = SyncStateORM(
                table_name=table_name,
                last_sync=last_sync,
            )
            self.session.add(obj)

        await self.session.commit()
        return obj

    async def delete_by_table_name(self, table_name: str) -> None:
        obj = await self.get_by_table_name(table_name)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()

    async def delete_all(self) -> None:
        states = await self.get_all()
        for state in states:
            await self.session.delete(state)

        await self.session.commit()
