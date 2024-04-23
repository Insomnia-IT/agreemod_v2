import logging

from typing import List

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.db.orm import ParticipationAppORM
from app.db.repos.base import BaseSqlaRepo
from app.errors import RepresentativeError
from app.models.participation import Participation


logger = logging.getLogger(__name__)


class ParticipationRepo(BaseSqlaRepo[ParticipationAppORM]):

    def get_query(
        self,
        notion_id: str = None,
        include_person: bool = True,
        include_direction: bool = True,
        include_role: bool = True,
        include_status: bool = True,
        include_participation: bool = True,
        limit: int = None,
        offset: int = None,
    ):
        query = select(ParticipationAppORM)
        if notion_id:
            query = query.filter(ParticipationAppORM.notion_id == notion_id)
        if include_person:
            query = query.options(joinedload(ParticipationAppORM.person))
        if include_direction:
            query = query.options(joinedload(ParticipationAppORM.direction))
        if include_role:
            query = query.options(joinedload(ParticipationAppORM.role))
        if include_status:
            query = query.options(joinedload(ParticipationAppORM.status))
        if include_participation:
            query = query.options(joinedload(ParticipationAppORM.participation))
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query

    async def retrieve(self, notion_id) -> Participation | None:
        result: ParticipationAppORM | None = await self.session.scalar(self.get_query(notion_id=notion_id))
        if result is None:
            return None
        return result.to_model()

    async def retrieve_all(self, page: int, page_size: int) -> List[Participation]:
        offset = (page - 1) * page_size
        results = await self.session.scalars(self.get_query(limit=page_size, offset=offset))
        return [result.to_model() for result in results]

    async def create(self, data: Participation):
        new_participation = ParticipationAppORM.to_orm(data)
        self.session.add(new_participation)
        try:
            await self.session.flush([new_participation])
        except IntegrityError as e:
            logger.error(f"{e.__class__.__name__}: {e}")
            # raise e
            raise RepresentativeError(title=f"participation with {data.notion_id=} already exists")
        return new_participation

    async def update(self, data: Participation):
        await self.session.merge(ParticipationAppORM.to_orm(data))
        await self.session.flush()

    async def delete(self, notion_id):
        await self.session.execute(delete(ParticipationAppORM).where(ParticipationAppORM.notion_id == notion_id))

    async def retrieve_many(self, filters: dict = None) -> list[Participation]:
        result = await self.session.scalars(self.get_query())
        return [x.to_model() for x in result]
