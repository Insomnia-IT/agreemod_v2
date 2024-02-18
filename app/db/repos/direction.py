from app.db.repos.base import BaseSqlaRepo
from app.models.direction import Direction


class DirectionRepo(BaseSqlaRepo):

    async def create(entity: Direction):
        pass

    async def retrieve(uuid: str) -> Direction:
        pass

    async def retrieve_many(filters) -> list[Direction]:
        pass
