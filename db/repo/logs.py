import datetime
import time

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.orm import LogsORM


class LogsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_log(
            self,
            table_name: str,
            operation: str,
            row_id: str,
            new_data: dict,
            author: str = None,
    ):
        """
        Add a new log entry to the database.
        """
        new_log = LogsORM(
            author=author,
            table_name=table_name,
            row_id=row_id,
            operation=operation,
            timestamp=datetime.datetime.now(),
            new_data=new_data,
        )
        self.session.add(new_log)
        await self.session.commit()

    async def get_log_by_id(self, log_id: int):
        """
        Retrieve a log entry by its ID.
        """
        result = await self.session.execute(
            select(LogsORM).where(LogsORM.id == log_id)
        )
        return result.scalars().first()

    async def get_all_logs(self):
        """
        Retrieve all log entries.
        """
        result = await self.session.execute(
            select(LogsORM)
        )
        return result.scalars().all()

    async def get_logs_by_table_and_time(self, table_name: str,
                                         from_timestamp: datetime):
        """
        Retrieve log entries by table name and from a specific timestamp.
        """
        result = await self.session.execute(
            select(LogsORM).where(
                (LogsORM.table_name == table_name) &
                (LogsORM.timestamp >= from_timestamp)
            )
        )
        return result.scalars().all()

    async def delete_log(self, log_id: int):
        """
        Delete a log entry based on its ID.
        """
        log_to_delete = await self.get_log_by_id(log_id)
        if log_to_delete:
            await self.session.delete(log_to_delete)
            await self.session.commit()
