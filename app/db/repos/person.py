from typing import List

from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from app.db.orm import PersonAppORM
from app.db.repos.base import BaseSqlaRepo
from app.errors import RepresentativeError
from app.models.person import Person
from app.schemas.person import PersonFiltersDTO


class PersonRepo(BaseSqlaRepo[PersonAppORM]):

    def query(
        self,
        notion_id: str = None,
        limit: int = None,
        page: int = None,
        filters: PersonFiltersDTO = None,
    ):
        query = select(PersonAppORM)
        if notion_id:
            query = query.filter_by(notion_id=notion_id)
        if page and limit:
            offset = (page - 1) * limit
            query = query.limit(limit).offset(offset)
        if filters and filters.strict:
            if filters.telegram:
                query = query.filter_by(telegram=filters.telegram)
            if filters.phone:
                query = query.filter_by(phone=filters.phone)
            if filters.email:
                query = query.filter_by(email=filters.email)
        elif filters:
            if filters.telegram:
                query = query.where(
                    PersonAppORM.telegram.ilike(f"%{filters.telegram}%")
                )
            if filters.phone:
                query = query.where(PersonAppORM.phone.ilike(f"%{filters.phone}%"))
            if filters.email:
                query = query.where(PersonAppORM.email.ilike(f"%{filters.email}%"))

        return query

    async def retrieve(self, notion_id, filters: PersonFiltersDTO) -> Person:
        filters.strict = True
        result: PersonAppORM = await self.session.scalar(
            self.query(notion_id=notion_id, filters=filters)
        )
        if result is None:
            return None
        return result.to_model()

    async def retrieve_all(self, page: int, page_size: int) -> List[Person]:
        results = await self.session.scalars(self.query(limit=page_size, page=page))
        if not results:
            return []
        return [result.to_model() for result in results]

    async def create(self, data: Person):
        new_person = PersonAppORM.to_orm(data)
        self.session.add(new_person)
        try:
            await self.session.flush([new_person])
        except IntegrityError as e:
            raise RepresentativeError(
                "Person already exists",
                detail=f"{e.__class__.__name__}: {e}",
                status_code=422,
            )
        return data

    async def update(self, data: Person):
        await self.session.merge(PersonAppORM.to_orm(data))
        await self.session.flush()

    async def delete_by_notion_id(self, notion_id):
        await self.session.execute(
            delete(PersonAppORM).where(PersonAppORM.notion_id == notion_id)
        )

    async def delete(self, id):
        await self.session.execute(delete(PersonAppORM).where(PersonAppORM.id == id))

    async def retrieve_many(
        self, filters: PersonFiltersDTO, page: int, page_size: int
    ) -> list[Person]:
        result = await self.session.scalars(
            self.query(filters=filters, page=page, limit=page_size)
        )
        return [x.to_model() for x in result]
