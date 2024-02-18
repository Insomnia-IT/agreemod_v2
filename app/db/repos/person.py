from app.db.repos.base import BaseSqlaRepo
from app.models.person import Person


class PersonRepo(BaseSqlaRepo):

    async def create(entity: Person):
        pass

    async def retrieve(uuid: str) -> Person:
        pass

    async def retrieve_many(filters) -> list[Person]:
        pass
