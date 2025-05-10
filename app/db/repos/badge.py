from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.db.orm import BadgeAppORM, BadgeDirectionsAppORM, DirectionAppORM, PersonAppORM
from app.db.repos.base import BaseSqlaRepo
from app.dto.direction import DirectionDTO
from app.models.badge import Badge
from app.models.direction import Direction
from app.schemas.badge import BadgeFilterDTO
from app.schemas.feeder.badge import Badge as FeederBadge


import logging
logger = logging.getLogger(__name__)

# TODO: перенести в модуль database!?
class BadgeRepo(BaseSqlaRepo[BadgeAppORM]):

    def query(
        self,
        id: UUID = None,
        idIn: List[UUID] = None,
        nocode_int_id: int = None,
        badge_number: str = None,
        phone: str = None,
        include_person: bool = False,
        include_directions: bool = False,
        include_parent: bool = False,
        limit: int = None,
        page: int = None,
        filters: BadgeFilterDTO = None,
        from_date: datetime = None,
    ):
        if include_directions:
            query = select(BadgeAppORM, BadgeDirectionsAppORM).join(BadgeAppORM.directions, isouter=True)
        else:
            query = select(BadgeAppORM)
        if id:
            query = query.where(BadgeAppORM.id == id)
        if idIn:
            query = query.where(BadgeAppORM.id.in_(idIn))
        if nocode_int_id:
            query = query.where(BadgeAppORM.nocode_int_id == nocode_int_id)
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
                selectinload(BadgeDirectionsAppORM.direction, )
            )
        if include_parent:
            query = query.options(selectinload(BadgeAppORM.parent))
        if from_date:
            query = query.filter(BadgeAppORM.last_updated > from_date)
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
                query = query.where(BadgeAppORM.parent_id == filters.infants)
        return query

    async def retrieve(
        self,
        id: UUID = None,
        nocode_int_id: int = None,
        badge_number: str = None,
        phone: str = None,
    ) -> Badge:
        if nocode_int_id or badge_number or phone or id:
            result: BadgeAppORM = await self.session.scalar(
                self.query(
                    id=id,
                    nocode_int_id=nocode_int_id,
                    badge_number=badge_number,
                    phone=phone,
                    include_directions=True,
                    include_parent=True,
                    include_person=True,
                )
            )
        else:
            return None
        if result is None:
            return None
        return result.to_model(include_person=True, include_directions=True, include_parent=True)

    async def retrieve_many(
        self,
        idIn: List[UUID] = None,
        page: int = None,
        page_size: int = None,
        filters: BadgeFilterDTO = None,
        include_directions: bool = False,
        include_parent: bool = False,
        include_person: bool = False,
        person_uuid: bool = False,
        from_date: datetime = None,
    ) -> List[Badge]:
        results = await self.session.scalars(
            self.query(
                idIn=idIn,
                page=page,
                limit=page_size,
                filters=filters,
                include_directions=include_directions,
                include_parent=include_parent,
                include_person=include_person,
                from_date=from_date,
            )
        )
        if not results:
            return []
        unique_results = results.unique()
        return [
            result.to_model(
                person_uuid=person_uuid,
                include_person=include_person,
                include_directions=include_directions,
                include_parent=include_parent,
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
                select(DirectionAppORM).filter_by(nocode_int_id=d.nocode_int_id if isinstance(d, Direction) else d)
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
            # Get directions for the badge
            directions: list[DirectionAppORM] = await self.session.scalars(
                select(DirectionAppORM).where(DirectionAppORM.id.in_(badge["directions"]))
            )
            # Check if badge exists
            badge_orm: BadgeAppORM = await self.session.scalar(
                select(BadgeAppORM).where(BadgeAppORM.id == b_id).options(selectinload(BadgeAppORM.parent))
            )
            
            if badge_orm:
                logger.info(f"Updating existing badge {b_id}")
                person_orm: PersonAppORM = await self.session.scalar(
                    select(PersonAppORM).where(PersonAppORM.id == badge.get("person",None))
                )
                logger.info(person_orm)
                badge["person"] = person_orm.nocode_int_id
                if badge.get("deleted", False) is True:
                    logger.info(f"Marking badge {b_id} as deleted")
                    if badge_orm.comment is not None:
                        badge_orm.comment += "///удалён"
                    else:
                        badge_orm.comment = "///удалён"
                    exist = None
                else:
                    exist = True
                    # Update badge properties
                    for x, y in badge.items():
                        if x not in ["id", "directions","person"] and y is not None:
                            logger.info(f"{x}, {y}")
                            if isinstance(y, Enum):
                                setattr(badge_orm, x, y.name) 
                            else:
                                setattr(badge_orm, x, y)

                    badge_orm.person = person_orm
                    # Update directions
                    for d in directions:
                        badge_dir = BadgeDirectionsAppORM()
                        badge_dir.direction = d
                        if d.nocode_int_id not in [x.direction_id for x in badge_orm.directions]:
                            badge_orm.directions.append(badge_dir)
                            badge_orm.last_updated = datetime.now()
                # Merge changes into session
                await self.session.merge(badge_orm)
            elif badge.get("deleted", False) is False:
                logger.info(f"Creating new badge {b_id}")
                person_orm: PersonAppORM = await self.session.scalar(
                    select(PersonAppORM).where(PersonAppORM.id == badge.get("person",None))
                )
                logger.info(person_orm)
                badge["person"] = person_orm.nocode_int_id
                # Create new badge
                badge["directions"] = [
                    DirectionDTO(id=x.id, name=x.name, type=x.type, nocode_int_id=x.nocode_int_id) for x in directions
                ]
                badge_orm = BadgeAppORM.to_orm(Badge.model_validate(badge))
                badge_orm.last_updated = datetime.now()
                # Add directions to new badge
                for d in directions:
                    badge_dir = BadgeDirectionsAppORM()
                    badge_dir.direction = d
                    if d.nocode_int_id not in [x.direction_id for x in badge_orm.directions]:
                        badge_orm.directions.append(badge_dir)
                print(badge_orm)
                self.session.add(badge_orm)
                exist = True
            elif badge.get("deleted", False) is True:
                logger.info(f"Badge {b_id} marked for deletion but doesn't exist")
                exist = None
            existing.append(exist)
            
            # Flush changes to database after each badge
            await self.session.commit()
            
        return existing

    async def delete(self, nocode_int_id):
        await self.session.execute(delete(BadgeAppORM).where(BadgeAppORM.nocode_int_id == nocode_int_id))
