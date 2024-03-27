from typing import List

from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from app.db.orm import ParticipationAppORM
from app.db.repos.base import BaseSqlaRepo
from app.models.participation import Participation


class ParticipationRepo(BaseSqlaRepo[ParticipationAppORM]):

    async def retrieve(self, notion_id) -> Participation:
        result: ParticipationAppORM = await self.session.scalar(
            select(ParticipationAppORM).filter_by(notion_id=notion_id)
        )
        if result is None:
            return None
        return result.to_model()

    async def retrieve_all(self, page: int, page_size: int) -> List[Participation]:
        offset = (page - 1) * page_size
        results = await self.session.scalars(
            select(ParticipationAppORM).limit(page_size).offset(offset)
        )
        if not results:
            return []
        return [result.to_model() for result in results]


    async def create(self, data: Participation):
        new_participation = ParticipationAppORM.to_orm(data)
        self.session.add(new_participation)
        try:
            await self.session.flush([new_participation])
        except IntegrityError as e:
            raise e
        return data

    async def update(self, data: Participation):
        await self.session.merge(ParticipationAppORM.to_orm(data))
        await self.session.flush()

    async def delete(self, notion_id):
        await self.session.execute(
            delete(ParticipationAppORM).where(ParticipationAppORM.notion_id == notion_id)
        )

    async def retrieve_many(self, filters: dict = None) -> list[Participation]:
        result = await self.session.scalars(select(ParticipationAppORM).filter_by(**filters))
        return [x.to_model() for x in result]
