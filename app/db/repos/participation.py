from typing import List

from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db.orm import ParticipationAppORM
from app.db.repos.base import BaseSqlaRepo
from app.models.participation import Participation

from app.errors import RepresentativeError

class ParticipationRepo(BaseSqlaRepo[ParticipationAppORM]):

    async def retrieve(self, notion_id) -> Participation | None:
        result: ParticipationAppORM | None = await self.session.query(ParticipationAppORM). \
            filter(ParticipationAppORM.notion_id == notion_id). \
            options(
            joinedload(ParticipationAppORM.person),
            joinedload(ParticipationAppORM.direction),
            joinedload(ParticipationAppORM.role),
            joinedload(ParticipationAppORM.status),
            joinedload(ParticipationAppORM.participation)
        ). \
            scalar()
        if result is None:
            return None
        return result.to_model()

    async def retrieve_all(self, page: int, page_size: int) -> List[Participation]:
        stmt = select(ParticipationAppORM).options(joinedload(ParticipationAppORM.person)).options(
            joinedload(ParticipationAppORM.direction)).options(joinedload(ParticipationAppORM.role)).options(
            joinedload(ParticipationAppORM.status)).options(joinedload(ParticipationAppORM.participation)).limit(
            page_size).offset((page - 1) * page_size)
        results = await self.session.execute(stmt)
        return [result[0].to_model() for result in results]

    async def create(self, data: Participation):
        new_participation = ParticipationAppORM.to_orm(data)
        self.session.add(new_participation)
        try:
            await self.session.flush([new_participation])
        except IntegrityError as e:
            logger.error(f"{e.__class__.__name__}: {e}")
            #raise e
            raise RepresentativeError(title=f"participation with {data.notion_id=} already exists")
        return new_participation

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
