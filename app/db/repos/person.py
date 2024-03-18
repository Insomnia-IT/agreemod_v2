from typing import List

from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from app.db.orm import PersonORM
from app.db.repos.base import BaseSqlaRepo
from app.models.person import Person


class PersonRepo(BaseSqlaRepo[PersonORM]):

    async def retrieve(self, notion_id) -> Person:
        result: PersonORM = await self.session.scalar(select(PersonORM).filter_by(notion_id=notion_id))
        if result is None:
            return None
        return result.to_model()

    async def retrieve_all(self, page: int, page_size: int) -> List[Person]:
        offset = (page - 1) * page_size
        results = await self.session.scalars(select(PersonORM).limit(page_size).offset(offset))
        if not results:
            return []
        return [result.to_model() for result in results]

    async def retrieve_by_telegram(self, telegram_username) -> Person:
        result = await self.session.scalar(select(PersonORM).filter_by(telegram=telegram_username))
        if result is None:
            return None
        return result.to_model()

    async def create(self, data: Person):
        new_person = PersonORM.to_orm(data)
        self.session.add(new_person)
        try:
            await self.session.flush([new_person])
        except IntegrityError as e:
            raise e
        return data

    async def update(self, data: Person):
        await self.session.merge(PersonORM.to_orm(data))
        await self.session.flush()

    async def delete(self, notion_id):
        await self.session.execute(delete(PersonORM).where(PersonORM.notion_id == notion_id))

    async def retrieve_many(self, filters: dict = None) -> list[Person]:
        result = await self.session.scalars(select(PersonORM).filter_by(**filters))
        return [x.to_model() for x in result]
