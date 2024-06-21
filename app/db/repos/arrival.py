from enum import Enum
import logging

from datetime import datetime

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

    async def retrieve(self, id, include_badge: bool) -> Arrival | None:
        query = select(ArrivalAppORM).filter_by(id=id)
        if include_badge:
            query = query.options(selectinload(ArrivalAppORM.badge))
        result = await self.session.scalar(query)
        if result is None:
            return None
        return result.to_model(include_badge=include_badge)

    async def retrieve_by_badge(self, badge_id, include_badge: bool):
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

    async def update_feeder(self, data: list[FeederArrival]) -> list[bool]:
        existing = []
        collected = {}
        for arrival in data:
            if arrival.id not in collected:
                collected.update({arrival.id: arrival.model_dump()})
            else:
                collected[arrival.id].update(arrival.model_dump(exclude_none=True))
        for a_id, arrival in collected.items():
            exist = False
            arrival_orm: ArrivalAppORM = await self.session.scalar(
                select(ArrivalAppORM).filter_by(id=a_id)
            )
            if arrival_orm:
                if arrival.get('deleted', False) is True:
                    await self.session.delete(arrival_orm)
                else:
                    exist = True
                    [
                        setattr(arrival_orm, x, y.name if isinstance(y, Enum) else y) for x,y
                        in arrival.items()
                        if x not in ['id'] and y is not None
                    ]
                    arrival_orm.last_updated = datetime.now()
                    await self.session.merge(arrival_orm)
            elif arrival.get('deleted', False) is False:
                arrival['badge'] = arrival['badge_id']
                arrival_orm = ArrivalAppORM.to_orm(Arrival.model_validate(arrival))
                arrival_orm.last_updated = datetime.now()
                self.session.add(arrival_orm)
                # await self.session.flush()
            existing.append(exist)
        return existing


    async def delete(self, id):
        await self.session.execute(delete(ArrivalAppORM).where(ArrivalAppORM.id == id))

    async def retrieve_many(self, filters: dict = None) -> list[Arrival]:
        result = await self.session.scalars(
            select(ArrivalAppORM)
            .filter_by(**filters)
            .options(
                selectinload(
                    ArrivalAppORM.badge,
                )
            )
        )
        return [x.to_model() for x in result]

    async def retrieve_all(self, page: int = None, page_size: int = None, from_date: datetime = None) -> list[Arrival]:
        query = select(ArrivalAppORM)
        if page and page_size:
            offset = (page - 1) * page_size
            query = query.limit(page_size).offset(offset)
        if from_date:
            query = query.where(ArrivalAppORM.last_updated > from_date)
        results = await self.session.scalars(query)
        if not results:
            return []
        return [result.to_model() for result in results]
