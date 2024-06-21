from datetime import datetime
from enum import Enum
from typing import List

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.db.orm import BadgeAppORM, BadgeDirectionsAppORM, DirectionAppORM
from app.db.repos.base import BaseSqlaRepo
from app.dto.direction import DirectionDTO
from app.models.badge import Badge
from app.models.direction import Direction
from app.schemas.badge import BadgeFilterDTO
from app.schemas.feeder.badge import Badge as FeederBadge


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
        from_date: datetime = None,
    ):
        if include_directions:
            query = select(BadgeAppORM, BadgeDirectionsAppORM).join(BadgeAppORM.directions)
        else:
            query = select(BadgeAppORM)
        if notion_id:
            query = query.where(BadgeAppORM.notion_id == notion_id)
        if badge_number:
            query = query.where(BadgeAppORM.number == badge_number)
        if phone:
            query = query.where(BadgeAppORM.phone == phone)
        if page and limit:
            offset = (page - 1) * limit
            query = query.limit(limit).offset(offset)
        if include_person:
            query = query.options(selectinload(BadgeAppORM.person))
        if include_directions:
            query = query.options(selectinload(BadgeAppORM.directions)).options(
                selectinload(BadgeDirectionsAppORM.direction)
            )
        if include_infant:
            query = query.options(selectinload(BadgeAppORM.infant))
        if from_date:
            query = query.where(BadgeAppORM.last_updated > from_date)
        if filters:
            if filters.batch:
                query = query.where(BadgeAppORM.batch == filters.batch)
            # if filters.direction:
            #     query = query.where([x.name for x in BadgeAppORM.directions])
            if filters.role:
                query = query.where(BadgeAppORM.role_code == filters.role)
            if filters.occupation:
                query = query.where(BadgeAppORM.occupation == filters.occupation)
            if filters.infants:
                query = query.where(BadgeAppORM.infant_id == filters.infants)
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
        from_date: datetime = None,
    ) -> List[Badge]:
        results = await self.session.scalars(
            self.query(
                page=page,
                limit=page_size,
                filters=filters,
                include_directions=include_directions,
                include_infant=include_infant,
                include_person=include_person,
                from_date=from_date,
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
        badge = BadgeAppORM.to_orm(data)
        for d in data.directions:
            direction = await self.session.scalar(
                select(DirectionAppORM).filter_by(notion_id=d.notion_id if isinstance(d, Direction) else d)
            )
            badge_dir = BadgeDirectionsAppORM()
            badge_dir.direction = direction
            badge.directions.append(badge_dir)
        await self.session.merge(badge)

    async def update_feeder(self, data: list[FeederBadge]) -> list[bool]:
        existing = []
        collected = {}
        for badge in data:
            if badge.id not in collected:
                collected.update({badge.id: badge.model_dump()})
            else:
                collected[badge.id].update(badge.model_dump(exclude_none=True))
                if collected[badge.id]["notion_id"] is None:
                    collected[badge.id]["notion_id"] = badge.id
        for b_id, badge in collected.items():
            exist = False
            directions: list[DirectionAppORM] = await self.session.scalars(
                select(DirectionAppORM).where(DirectionAppORM.notion_id.in_(badge["directions"]))
            )
            badge_orm: BadgeAppORM = await self.session.scalar(
                select(BadgeAppORM).where(BadgeAppORM.notion_id == b_id).options(selectinload(BadgeAppORM.infant))
            )
            if badge_orm:
                if badge.get("deleted", False) is True:
                    if badge_orm.comment is not None:
                        badge_orm.comment += "///удалён"
                    else:
                        badge_orm.comment = "///удалён"
                    exist = None
                else:
                    exist = True
                    [
                        setattr(badge_orm, x, y.name if isinstance(y, Enum) else y)
                        for x, y in badge.items()
                        if x not in ["id", "directions"] and y is not None
                    ]
                    for d in directions:
                        badge_dir = BadgeDirectionsAppORM()
                        badge_dir.direction = d
                        if d.notion_id not in [x.direction_id for x in badge_orm.directions]:
                            badge_orm.directions.append(badge_dir)
                            badge_orm.last_updated = datetime.now()
                await self.session.merge(badge_orm)
            elif badge.get("deleted", False) is False:
                badge["directions"] = [
                    DirectionDTO(id=x.id, name=x.name, type=x.type, notion_id=x.notion_id) for x in directions
                ]
                badge_orm = BadgeAppORM.to_orm(Badge.model_validate(badge))
                badge_orm.last_updated = datetime.now()
                for d in directions:
                    badge_dir = BadgeDirectionsAppORM()
                    badge_dir.direction = d
                    if d.notion_id not in [x.direction_id for x in badge_orm.directions]:
                        badge_orm.directions.append(badge_dir)
                self.session.add(badge_orm)
            elif badge.get("deleted", False) is True:
                exist = None
            existing.append(exist)
        return existing

    async def delete(self, notion_id):
        await self.session.execute(delete(BadgeAppORM).where(BadgeAppORM.notion_id == notion_id))
