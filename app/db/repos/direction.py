import logging
from typing import List
from uuid import UUID

from datetime import datetime

from sqlalchemy import delete, select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.db.orm import BadgeDirectionsAppORM, DirectionAppORM
from app.db.repos.base import BaseSqlaRepo
from app.errors import RepresentativeError
from app.models.direction import Direction


logger = logging.getLogger(__name__)


class DirectionRepo(BaseSqlaRepo[DirectionAppORM]):

    async def create(self, data: Direction):
        new_direction = DirectionAppORM.to_orm(data)
        self.session.add(new_direction)
        try:
            await self.session.flush([new_direction])
        except IntegrityError as e:
            logger.error(f"{e.__class__.__name__}: {e}")
            raise RepresentativeError(title=f"direction with {data.nocode_int_id=} already exists")
        return new_direction

    async def retrieve(self, nocode_int_id, include_badges: bool = True) -> Direction:
        result = await self.session.scalar(
            select(DirectionAppORM, BadgeDirectionsAppORM)
            .where(DirectionAppORM.nocode_int_id == nocode_int_id)
            .options(selectinload(DirectionAppORM.badges))
            .options(selectinload(BadgeDirectionsAppORM.badge))
        )
        if result is None:
            return None
        return result.to_model(include_badges=include_badges)

    async def update(self, data: Direction):
        orm = DirectionAppORM.to_orm(data)
        await self.session.merge(orm)
        await self.session.flush([orm])

    async def delete(self, nocode_int_id):
        await self.session.execute(delete(DirectionAppORM).where(DirectionAppORM.nocode_int_id == nocode_int_id))

    async def retrieve_all(self, from_date: datetime = None) -> list[Direction]:
        query = select(DirectionAppORM)
        if from_date:
            query = query.where(or_(DirectionAppORM.last_updated > from_date, DirectionAppORM.last_updated.is_(None)))
        result = await self.session.scalars(query)
        return [x.to_model() for x in result]

    def query(
        self,
        idIn: List[UUID] = None,
        include_badges: bool = False,
    ):
        query = select(DirectionAppORM)
        if idIn:
            query = query.where(DirectionAppORM.id.in_(idIn))
        if include_badges:
            query = query.options(selectinload(DirectionAppORM.badges)).options(selectinload(BadgeDirectionsAppORM.badge))
        return query

    async def retrieve_many(self, idIn: List[UUID] = None, include_badges: bool = False) -> list[Direction]:
        result = await self.session.scalars(self.query(idIn=idIn, include_badges=include_badges))
        return [x.to_model(include_badges=include_badges) for x in result]
