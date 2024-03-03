import logging

from sqlalchemy import delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.db.orm import DirectionORM
from app.db.repos.base import BaseSqlaRepo
from app.errors import RepresentativeError
from app.models.direction import Direction

logger = logging.getLogger(__name__)


class DirectionRepo(BaseSqlaRepo):
    def __init__(self, session: AsyncSession | Session):
        super().__init__(session)
        self.session = session

    async def create(self, data: Direction):
        new_direction = DirectionORM.to_orm(data)
        self.session.add(new_direction)
        try:
            await self.session.flush([new_direction])
        except IntegrityError as e:
            logger.critical(e)
            raise RepresentativeError(title=f"direction with {data.notion_id=} already exists")
        return new_direction

    def create_sync(self, data: Direction):
        """
        Синхронная запись данных
        """
        self.session.add(DirectionORM.to_orm(data))
        self.session.commit()

    def delete_and_create(self, data: Direction):
        """
        Синхронная запись данных с удалением старых данных
        """
        existing_direction = self.session.query(DirectionORM).filter_by(notion_id=data.notion_id).first()

        if existing_direction is not None:
            self.session.delete(existing_direction)

        self.session.add(DirectionORM.to_orm(data))
        self.session.commit()

    async def get_by_id(self, notion_id):
        result = await self.session.execute(select(DirectionORM).filter_by(notion_id=notion_id))
        return result.scalars().first()

    async def read(self, notion_id) -> Direction | None:
        direction = await self.get_by_id(notion_id)
        if direction:
            return direction.to_model()
        return None

    async def update(self, notion_id, data: Direction):
        await self.session.execute(
            update(DirectionORM).
            where(DirectionORM.notion_id == notion_id).
            values(**data.dict())
        )
        await self.session.commit()

    async def delete(self, notion_id):
        await self.session.execute(
            delete(DirectionORM).
            where(DirectionORM.notion_id == notion_id)
        )
        await self.session.commit()

    async def retrieve(self, uuid: str) -> Direction | None:
        result = await self.session.execute(select(DirectionORM).filter_by(notion_id=uuid))
        direction = result.scalars().first()
        if direction:
            return direction.to_model()
        return None

    async def retrieve_many(self, filters) -> list[Direction]:
        result = await self.session.execute(select(DirectionORM).filter_by(**filters))
        directions = result.scalars().all()
        direction_models = []
        for direction in directions:
            direction_model = direction.to_model()
            direction_models.append(direction_model)
        return direction_models

    async def retrieve_all(self) -> list[Direction]:
        result = await self.session.execute(select(DirectionORM))
        directions = result.scalars().all()
        direction_models = []
        for direction in directions:
            direction_model = direction.to_model()
            direction_models.append(direction_model)
        return direction_models
