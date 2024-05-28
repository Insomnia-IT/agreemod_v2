from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from updater.src.db.orm.participation import ParticipationUpdORM
from updater.src.db.repos.base import BaseSqlaRepo
from updater.src.notion.models.participation import Participation


class ParticipationRepo(BaseSqlaRepo[ParticipationUpdORM]):
    @staticmethod
    async def retrieve_all(session: AsyncSession) -> list[Participation]:
        results = await session.scalars(select(ParticipationUpdORM))
        data = [i.to_model() for i in results]
        return data
