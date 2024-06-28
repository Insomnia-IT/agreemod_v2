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

    async def get_badges_by_notion_ids(self, notion_ids: List[UUID]) -> List[BadgeORM]:
        """Получить бейджи по списку notion_id."""
        if not notion_ids:
            return []

        notion_ids_str = [str(notion_id) for notion_id in notion_ids]
        if not notion_ids_str:
            return []

        logger.info(f"notion_ids_str: {notion_ids_str}")

        query = select(BadgeORM).where(BadgeORM.notion_id.in_(notion_ids_str))
        logger.info(f"query: {query}")

        result = await self.session.execute(query)

        badges = result.scalars().all()

        # Логирование результатов
        logger.info(f"Found badges: {badges}")

        return badges
