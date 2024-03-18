import logging

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.db.orm import DirectionORM
from app.db.repos.base import BaseSqlaRepo
# from app.errors import RepresentativeError
from app.models.direction import Direction


logger = logging.getLogger(__name__)


class DirectionRepo(BaseSqlaRepo):

    async def create(self, data: Direction):
        new_direction = DirectionORM.to_orm(data)
        self.session.add(new_direction)
        try:
            await self.session.flush([new_direction])
        except IntegrityError as e:
            logger.error(f"{e.__class__.__name__}: {e}")
            raise e
            # raise RepresentativeError(title=f"direction with {data.notion_id=} already exists")
        return new_direction

    # def create_sync(self, data: Direction):
    #     """
    #     Синхронная запись данных
    #     """
    #     self.session.add(DirectionORM.to_orm(data))

    # def delete_and_create_sync(self, data: Direction):
    #     """
    #     Синхронная запись данных с удалением старых
    #     """
    #     existing_direction = self.session.query(DirectionORM).filter_by(notion_id=data.notion_id).first()

    #     if existing_direction is not None:
    #         self.session.delete(existing_direction)

    #     self.session.add(DirectionORM.to_orm(data))
    #     self.session.flush([existing_direction])

    async def retrieve(self, notion_id):
        result = await self.session.scalar(
            select(DirectionORM).filter_by(notion_id=notion_id).options(joinedload(DirectionORM.direction_type))
        )
        if result is None:
            return None
        return result.to_model()

    async def update(self, data: Direction):
        orm = DirectionORM.to_orm(data)
        await self.session.merge(orm)
        await self.session.flush([orm])

    async def delete(self, notion_id):
        await self.session.execute(delete(DirectionORM).where(DirectionORM.notion_id == notion_id))

    async def retrieve_many(self, filters: dict = None) -> list[Direction]:
        result = await self.session.scalars(
            select(DirectionORM).filter_by(**filters).options(joinedload(DirectionORM.direction_type))
        )
        return [x.to_model() for x in result]

    async def retrieve_all(self) -> list[Direction]:
        result = await self.session.scalars(select(DirectionORM).options(joinedload(DirectionORM.direction_type)))
        return [x.to_model() for x in result]
