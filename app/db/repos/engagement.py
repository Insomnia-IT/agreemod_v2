import logging

from datetime import datetime
from typing import List

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.db.orm import EngagementAppORM
from app.db.repos.base import BaseSqlaRepo
from app.errors import RepresentativeError
from app.models.engagement import Engagement


logger = logging.getLogger(__name__)


class EngagementRepo(BaseSqlaRepo[EngagementAppORM]):

    def get_query(
        self,
        id: str = None,
        include_person: bool = True,
        include_direction: bool = True,
        limit: int = None,
        page: int = None,
        from_date: datetime = None,
    ):
        query = select(EngagementAppORM)
        if id:
            query = query.filter(EngagementAppORM.id == id)
        if include_person:
            query = query.options(selectinload(EngagementAppORM.person))
        if include_direction:
            query = query.options(selectinload(EngagementAppORM.direction))
        if page and limit:
            offset = (page - 1) * limit
            query = query.limit(limit).offset(offset)
        if from_date:
            query = query.where(EngagementAppORM.last_updated > from_date)
        return query

    async def retrieve(self, id, include_person: bool, include_direction: bool) -> Engagement | None:
        result: EngagementAppORM | None = await self.session.scalar(
            self.get_query(
                id=id,
                include_person=include_person,
                include_direction=include_direction,
            )
        )
        if result is None:
            return None
        return result.to_model(include_person=include_person, include_direction=include_direction)

    async def retrieve_personal(self, person_id: int, include_direction: bool = False) -> list[Engagement]:
        results = await self.session.scalars(
            self.get_query(include_direction=include_direction).filter(EngagementAppORM.person_id == person_id)
        )
        return [result.to_model(include_direction=include_direction) for result in results]

    async def retrieve_all(
        self,
        page: int = None,
        page_size: int = None,
        include_direction: bool = False,
        include_person: bool = False,
        uuid_ids: bool = False,
        from_date: datetime = None,
    ) -> List[Engagement]:
        results = await self.session.scalars(
            self.get_query(
                limit=page_size,
                page=page,
                include_person=include_person,
                include_direction=include_direction,
                from_date=from_date,
            )
        )
        return [
            result.to_model(include_person=include_person, include_direction=include_direction, uuid_ids=uuid_ids) for result in results
        ]

    async def create(self, data: Engagement):
        new_engagement = EngagementAppORM.to_orm(data)
        self.session.add(new_engagement)
        try:
            await self.session.flush([new_engagement])
        except IntegrityError as e:
            logger.error(f"{e.__class__.__name__}: {e}")
            # raise e
            raise RepresentativeError(title=f"engagement with {data.id=} already exists")
        return new_engagement

    async def update(self, data: Engagement):
        await self.session.merge(EngagementAppORM.to_orm(data))
        await self.session.flush()

    async def delete(self, id):
        await self.session.execute(delete(EngagementAppORM).where(EngagementAppORM.id == id))

    async def retrieve_many(self, filters: dict = None) -> list[Engagement]:
        result = await self.session.scalars(self.get_query())
        return [x.to_model() for x in result]
