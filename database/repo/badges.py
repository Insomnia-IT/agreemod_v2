import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import UUID

from typing import List
from database.orm.badge import BadgeORM

logger = logging.getLogger(__name__)


class BadgeRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_badges(self) -> List[BadgeORM]:
        """Получить все бейджи без пагинации."""
        result = await self.session.execute(select(BadgeORM))
        return result.scalars().all()

    async def get_badges_by_nocode_int_ids(self, nocode_int_ids: List[int]) -> List[BadgeORM]:
        """Получить бейджи по списку nocode_int_id."""
        if not nocode_int_ids:
            return []

        nocode_int_ids_str = [str(nocode_int_id) for nocode_int_id in nocode_int_ids]
        if not nocode_int_ids_str:
            return []

        logger.info(f"nocode_int_ids_str: {nocode_int_ids_str}")

        query = select(BadgeORM).where(BadgeORM.nocode_int_id.in_(nocode_int_ids_str))
        logger.info(f"query: {query}")

        result = await self.session.execute(query)

        badges = result.scalars().all()

        # Логирование результатов
        logger.info(f"Found badges: {badges}")

        return badges
