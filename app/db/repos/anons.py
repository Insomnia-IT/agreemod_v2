from sqlalchemy.future import select

from app.db.orm import AnonsAppORM
from app.db.repos.base import BaseSqlaRepo
from app.models.badge import Anons


class AnonsRepo(BaseSqlaRepo[AnonsAppORM]):

    def query(
        self,
        batch,
    ):
        query = select(AnonsAppORM).filter_by(batch=batch)
        return query

    async def retrieve_batch(self, batch: str) -> list[Anons]:
        result: list[AnonsAppORM] = await self.session.scalars(
            self.query(batch)
        )
        if result is None:
            return []
        return [x.to_model() for x in result]