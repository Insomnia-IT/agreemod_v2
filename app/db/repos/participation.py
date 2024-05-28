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
        id: str = None,
        include_person: bool = True,
        include_direction: bool = True,
        limit: int = None,
        offset: int = None,
    ):
        query = select(ParticipationAppORM)
        if id:
            query = query.filter(ParticipationAppORM.id == id)
        if include_person:
            query = query.options(joinedload(ParticipationAppORM.person))
        if include_direction:
            query = query.options(joinedload(ParticipationAppORM.direction))
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query

    async def retrieve(
        self, id, include_person: bool, include_direction: bool
    ) -> Participation | None:
        result: ParticipationAppORM | None = await self.session.scalar(
            self.get_query(
                id=id,
                include_person=include_person,
                include_direction=include_direction,
            )
        )
        if result is None:
            return None
        return result.to_model(
            include_person=include_person, include_direction=include_direction
        )

    async def retrieve_personal(
        self, person_id: str, include_direction: bool
    ) -> list[Participation]:
        results = await self.session.scalars(
            self.get_query(include_direction=include_direction).filter(
                ParticipationAppORM.person_id == person_id
            )
        )
        return [
            result.to_model(include_direction=include_direction) for result in results
        ]

    async def retrieve_all(
        self,
        page: int,
        page_size: int,
        include_direction: bool = False,
        include_person: bool = False,
    ) -> List[Participation]:
        offset = (page - 1) * page_size
        results = await self.session.scalars(
            self.get_query(
                limit=page_size,
                offset=offset,
                include_person=include_person,
                include_direction=include_direction,
            )
        )
        return [
            result.to_model(
                include_person=include_person, include_direction=include_direction
            )
            for result in results
        ]

    async def create(self, data: Participation):
        new_participation = ParticipationAppORM.to_orm(data)
        self.session.add(new_participation)
        try:
            await self.session.flush([new_participation])
        except IntegrityError as e:
            logger.error(f"{e.__class__.__name__}: {e}")
            # raise e
            raise RepresentativeError(
                title=f"participation with {data.id=} already exists"
            )
        return new_participation

    async def update(self, data: Participation):
        await self.session.merge(ParticipationAppORM.to_orm(data))
        await self.session.flush()

    async def delete(self, id):
        await self.session.execute(
            delete(ParticipationAppORM).where(ParticipationAppORM.id == id)
        )

    async def retrieve_many(self, filters: dict = None) -> list[Participation]:
        result = await self.session.scalars(self.get_query())
        return [x.to_model() for x in result]
