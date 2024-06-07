import logging
from typing import List

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.db.orm import BadgeAppORM
from app.db.repos.base import BaseSqlaRepo
from app.models.badge import Badge

logger = logging.getLogger(__name__)


class BadgeRepo(BaseSqlaRepo[BadgeAppORM]):

    async def retrieve(self, notion_id) -> Badge:
        result: BadgeAppORM = await self.session.scalar(
            select(BadgeAppORM)
            .filter_by(notion_id=notion_id)
            .options(joinedload(BadgeAppORM.person, BadgeAppORM.direction))
        )
        if result is None:
            return None
        return result.to_model()

    async def retrieve_all(self, page: int, page_size: int) -> List[Badge]:
        offset = (page - 1) * page_size
        results = await self.session.scalars(
            select(BadgeAppORM)
            .limit(page_size)
            .offset(offset)
            .options(joinedload(BadgeAppORM.person, BadgeAppORM.direction))
        )
        if not results:
            return []
        return [result.to_model() for result in results]

    async def retrieve_all_2(self, page: int, page_size: int) -> list[Badge]:
        offset = (page - 1) * page_size
        result_scalars = await self.session.scalars(
            select(BadgeAppORM)
            .limit(page_size)
            .offset(offset)
        )
        results = result_scalars.all()

        if not results:
            return []

        processed_results = []
        for result in results:
            try:
                processed_results.append(result.to_model_2())
            except Exception as e:
                logger.critical(f"Error processing result {result}: {e}")

        return processed_results

    async def retrieve_by_phone(self, phone) -> Badge:
        result = await self.session.scalar(
            select(BadgeAppORM)
            .filter_by(phone=phone)
            .options(joinedload(BadgeAppORM.person, BadgeAppORM.direction))
        )
        if result is None:
            return None
        return result.to_model()

    async def create(self, data: Badge):
        new_badge = BadgeAppORM.to_orm(data)
        self.session.add(new_badge)
        try:
            await self.session.flush([new_badge])
        except IntegrityError as e:
            raise e
        return data

    async def update(self, data: Badge):
        await self.session.merge(BadgeAppORM.to_orm(data))
        await self.session.flush()

    async def update_2(self, data: Badge):
        """
        TODO: костыль для feeder
        """
        obj = BadgeAppORM.to_orm_2(data)
        await self.session.merge(obj)
        await self.session.flush()

    async def delete(self, notion_id):
        await self.session.execute(
            delete(BadgeAppORM).where(BadgeAppORM.notion_id == notion_id)
        )

    async def retrieve_many(self, filters: dict = None) -> list[Badge]:
        result = await self.session.scalars(
            select(BadgeAppORM)
            .filter_by(**filters)
            .options(joinedload(BadgeAppORM.person, BadgeAppORM.direction))
        )
        return [x.to_model() for x in result]
