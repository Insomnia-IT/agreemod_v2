import logging
from typing import List
from uuid import UUID

from datetime import datetime
from enum import Enum

from database.orm.badge import BadgeORM
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.db.orm import ArrivalAppORM
from app.db.repos.base import BaseSqlaRepo
from app.errors import RepresentativeError
from app.models.arrival import Arrival
from app.schemas.feeder.arrival import Arrival as FeederArrival


logger = logging.getLogger(__name__)


class ArrivalRepo(BaseSqlaRepo[ArrivalAppORM]):

    async def create(self, data: Arrival):
        new_arrival = ArrivalAppORM.to_orm(data)
        self.session.add(new_arrival)
        try:
            await self.session.flush([new_arrival])
        except IntegrityError as e:
            logger.error(f"{e.__class__.__name__}: {e}")
            # raise e
            raise RepresentativeError(title=f"arrival with {data.id=} already exists")
        return new_arrival

    async def retrieve(self, id, include_badge: bool = False) -> Arrival | None:
        query = select(ArrivalAppORM).filter_by(id=id)
        if include_badge:
            query = query.options(selectinload(ArrivalAppORM.badge))
        result = await self.session.scalar(query)
        if result is None:
            return None
        return result.to_model(include_badge=include_badge)

    async def retrieve_by_badge(self, badge_id, include_badge: bool = False):
        query = select(ArrivalAppORM).filter_by(badge_id=badge_id)
        if include_badge:
            query = query.options(selectinload(ArrivalAppORM.badge))
        result = await self.session.scalar(query)
        if result is None:
            return None
        return result.to_model(include_badge=include_badge)

    async def update(self, data: Arrival):
        orm = ArrivalAppORM.to_orm(data)
        await self.session.merge(orm)
        await self.session.flush([orm])

    async def update_feeder(self, data: list[FeederArrival]) -> list[ArrivalAppORM]:
        created = []
        deleted = []
        collected = {}
        for arrival in data:
            if arrival.id not in collected:
                collected.update({arrival.id: arrival.model_dump()})
            else:
                collected[arrival.id].update(arrival.model_dump(exclude_none=True))
        for a_id, arrival in collected.items():
            arrival_orm: ArrivalAppORM = await self.session.scalar(select(ArrivalAppORM).filter_by(id=a_id))
            if arrival_orm:
                if arrival.get("deleted", False) is True:
                    deleted.append(arrival_orm.coda_index)
                    await self.delete(arrival_orm.id)
                    created.append(None)
                else:
                    [
                        setattr(arrival_orm, x, y.name if isinstance(y, Enum) else y)
                        for x, y in arrival.items()
                        if x not in ["id"] and y is not None
                    ]
                    arrival_orm.last_updated = datetime.now()
                    await self.session.merge(arrival_orm)
                    created.append(arrival_orm)
            elif arrival.get("deleted", False) is False:
                arrival["badge"] = arrival["badge_id"]
                badge = await self.session.scalar(select(BadgeORM).where(BadgeORM.nocode_int_id == arrival['badge']))
                if badge:
                    arrival_orm = ArrivalAppORM.to_orm(Arrival.model_validate(arrival))
                    arrival_orm.last_updated = datetime.now()
                    self.session.add(arrival_orm)
                    await self.session.flush([arrival_orm])
                    created.append(arrival_orm)
            elif arrival.get("deleted", False) is True:
                created.append(None)
                # await self.session.flush()
        return created, deleted

    async def delete(self, id):
        await self.session.execute(delete(ArrivalAppORM).where(ArrivalAppORM.id == id))

    def query(
        self,
        idIn: List[UUID] = None,
        filters: dict = None,
        include_badge: bool = False,
    ):
        query = select(ArrivalAppORM)
        if idIn:
            query = query.where(ArrivalAppORM.id.in_(idIn))
        if filters:
            query = query.filter_by(**filters)
        if include_badge:
            query = query.options(selectinload(ArrivalAppORM.badge))
        return query

    async def retrieve_many(self, idIn: List[UUID] = None, filters: dict = None, include_badge: bool = False) -> list[Arrival]:
        result = await self.session.scalars(self.query(idIn=idIn, filters=filters, include_badge=include_badge))
        return [x.to_model(include_badge=include_badge) for x in result]

    async def retrieve_all(self, page: int = None, page_size: int = None, from_date: datetime = None, badge_uuid: bool = None) -> list[Arrival]:
        query = select(ArrivalAppORM)
        if page and page_size:
            offset = (page - 1) * page_size
            query = query.limit(page_size).offset(offset)
        if from_date:
            query = query.where(ArrivalAppORM.last_updated > from_date)
        if badge_uuid:
            query = query.options(selectinload(ArrivalAppORM.badge))
        results = await self.session.scalars(query)
        if not results:
            return []
        return [result.to_model(include_badge=True) for result in results]
