from typing import List

from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from app.db.orm import BadgeAppORM
from app.db.repos.base import BaseSqlaRepo
from app.models.badge import Badge


class BadgeRepo(BaseSqlaRepo[BadgeAppORM]):

    async def retrieve(self, notion_id) -> Badge:
        result: BadgeAppORM = await self.session.scalar(
            select(BadgeAppORM).filter_by(notion_id=notion_id)
        )
        if result is None:
            return None
        return result.to_model()

    async def retrieve_all(self, page: int, page_size: int) -> List[Badge]:
        offset = (page - 1) * page_size
        results = await self.session.scalars(
            select(BadgeAppORM).limit(page_size).offset(offset)
        )
        if not results:
            return []
        return [result.to_model() for result in results]

    async def retrieve_by_phone(self, phone) -> Badge:
        result = await self.session.scalar(
            select(BadgeAppORM).filter_by(phone=phone)
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

    async def delete(self, notion_id):
        await self.session.execute(
            delete(BadgeAppORM).where(BadgeAppORM.notion_id == notion_id)
        )

    async def retrieve_many(self, filters: dict = None) -> list[Badge]:
        result = await self.session.scalars(select(BadgeAppORM).filter_by(**filters))
        return [x.to_model() for x in result]
