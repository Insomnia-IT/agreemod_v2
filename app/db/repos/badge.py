from typing import List

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.db.orm import BadgeAppORM
from app.db.repos.base import BaseSqlaRepo
from app.models.badge import Badge
from app.schemas.badge import BadgeFilterDTO


class BadgeRepo(BaseSqlaRepo[BadgeAppORM]):

    def query(
        self,
        notion_id: str = None,
        badge_number: str = None,
        phone: str = None,
        include_person: bool = False,
        include_directions: bool = False,
        include_infant: bool = False,
        limit: int = None,
        page: int = None,
        filters: BadgeFilterDTO = None,
    ):
        query = select(BadgeAppORM)
        if notion_id:
            query = query.filter_by(notion_id=notion_id)
        if badge_number:
            query = query.filter_by(badge_number=badge_number)
        if phone:
            query = query.filter_by(phone=phone)
        if page and limit:
            offset = (page - 1) * limit
            query = query.limit(limit).offset(offset)
        if include_person:
            query = query.options(joinedload(BadgeAppORM.person))
        if include_directions:
            query = query.options(joinedload(BadgeAppORM.directions))
        if include_infant:
            query = query.options(joinedload(BadgeAppORM.infant))
        if filters:
            if filters.batch:
                query = query.filter_by(batch=filters.batch)
            if filters.color:
                query = query.filter_by(color=filters.color)
            # if filters.direction:
            #     query = query.where([x.name for x in BadgeAppORM.directions])
            if filters.role:
                query = query.filter_by(role=filters.role)
            if filters.occupation:
                query = query.filter_by(occupation=filters.occupation)
            if filters.infants:
                query = query.filter_by(infant_id=filters.infants)
        return query

    async def retrieve(
        self,
        notion_id: str = None,
        badge_number: str = None,
        phone: str = None,
    ) -> Badge:
        if notion_id or badge_number or phone:
            result: BadgeAppORM = await self.session.scalar(
                self.query(
                    notion_id=notion_id,
                    badge_number=badge_number,
                    phone=phone,
                    include_directions=True,
                    include_infant=True,
                    include_person=True,
                )
            )
        else:
            return None
        if result is None:
            return None
        return result.to_model(include_person=True, include_directions=True, include_infant=True)

    async def retrieve_many(
        self,
        page: int = None,
        page_size: int = None,
        filters: BadgeFilterDTO = None,
        include_directions: bool = False,
        include_infant: bool = False,
        include_person: bool = False,
    ) -> List[Badge]:
        results = await self.session.scalars(
            self.query(
                page=page,
                limit=page_size,
                filters=filters,
                include_directions=include_directions,
                include_infant=include_infant,
                include_person=include_person,
            )
        )
        if not results:
            return []
        unique_results = results.unique()
        return [
            result.to_model(
                include_person=include_person,
                include_directions=include_directions,
                include_infant=include_infant,
            )
            for result in unique_results
        ]

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
        await self.session.execute(delete(BadgeAppORM).where(BadgeAppORM.notion_id == notion_id))
