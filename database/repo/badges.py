from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from database.orm.badge import BadgeORM


class BadgeRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_badges(self) -> List[BadgeORM]:
        """Получить все бейджи без пагинации."""
        result = await self.session.execute(select(BadgeORM))
        return result.scalars().all()
