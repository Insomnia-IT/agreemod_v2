
from sqlalchemy.exc import IntegrityError

from app.db.orm import LogsAppORM
from app.db.repos.base import BaseSqlaRepo
from app.models.logging import Logs

class LogsRepo(BaseSqlaRepo[LogsAppORM]):
    async def add_log(self, data: Logs):
        new_row = LogsAppORM.to_orm(data)
        self.session.add(new_row)
        try:
            await self.session.flush([new_row])
        except IntegrityError as e:
            raise e
        return data

    async def retrieve_logs(
        self,
        range: tuple[int, int] = None,
        last: int = None,
        author: str = None
    ):
        pass