from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from updater.src.db.orm.engagement import EngagementUpdORM
from updater.src.db.repos.base import BaseSqlaRepo
from updater.src.notion.models.engagement import Engagement


class EngagementRepo(BaseSqlaRepo[EngagementUpdORM]):
    @staticmethod
    async def retrieve_all(session: AsyncSession) -> list[Engagement]:
        results = await session.scalars(select(EngagementUpdORM))
        data = [i.to_model() for i in results]
        return data
