import logging

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.db.orm import ArrivalAppORM
from app.db.repos.base import BaseSqlaRepo
from app.errors import RepresentativeError
from app.models.arrival import Arrival


logger = logging.getLogger(__name__)


class ArrivalRepo(BaseSqlaRepo[ArrivalAppORM]):

    async def create(self, data: Arrival):
        new_arrival = ArrivalAppORM.to_orm(data)
        self.session.add(new_arrival)
        try:
            await self.session.flush([new_arrival])
        except IntegrityError as e:
            logger.error(f"{e.__class__.__name__}: {e}")
            raise RepresentativeError(title=f"arrival with {data.id=} already exists")
        return new_arrival

    async def retrieve(self, id):
        result = await self.session.scalar(
            select(ArrivalAppORM)
            .filter_by(id=id)
            .options(
                joinedload(
                    ArrivalAppORM.badge,
                )
            )
        )
        if result is None:
            return None
        return result.to_model()

    async def update(self, data: Arrival):
        orm = ArrivalAppORM.to_orm(data)
        await self.session.merge(orm)
        await self.session.flush([orm])

    async def delete(self, id):
        await self.session.execute(delete(ArrivalAppORM).where(ArrivalAppORM.id == id))

    async def retrieve_many(self, filters: dict = None) -> list[Arrival]:
        result = await self.session.scalars(
            select(ArrivalAppORM)
            .filter_by(**filters)
            .options(
                joinedload(
                    ArrivalAppORM.badge
                )
            )
        )
        return [x.to_model() for x in result]

    async def retrieve_all(self) -> list[Arrival]:
        result = await self.session.scalars(select(ArrivalAppORM))
        return [x.to_model() for x in result]
