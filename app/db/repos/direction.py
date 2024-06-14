import logging

from datetime import datetime

from sqlalchemy import delete, select
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
            raise RepresentativeError(title=f"direction with {data.notion_id=} already exists")
        return new_direction

    async def retrieve(self, notion_id, include_badges: bool = True) -> Direction:
        result = await self.session.scalar(
            select(DirectionAppORM, BadgeDirectionsAppORM)
            .where(DirectionAppORM.notion_id == notion_id)
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

    async def delete(self, notion_id):
        await self.session.execute(delete(DirectionAppORM).where(DirectionAppORM.notion_id == notion_id))

    async def retrieve_all(self, from_date: datetime = None) -> list[Direction]:
        query = select(DirectionAppORM)
        if from_date:
            query = query.where(DirectionAppORM.last_updated > from_date)
        result = await self.session.scalars(query)
        return [x.to_model() for x in result]
