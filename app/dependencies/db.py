import logging

from typing import AsyncGenerator, Callable, Type, TypeVar

from db.meta import async_session
from db.repos.base import BaseSqlaRepo
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


_logger = logging.getLogger(__name__)


async def get_sqla_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        _logger.info("init SQLA session: %s", session)
        yield session
    _logger.info("SQLA session closed %s", session)


TSqlaRepo = TypeVar("TSqlaRepo", bound=BaseSqlaRepo)


def get_sqla_repo(repo_type: Type[TSqlaRepo]) -> Callable[[AsyncSession], TSqlaRepo]:
    def func(
        conn: AsyncSession = Depends(get_sqla_session, use_cache=True)
    ) -> TSqlaRepo:
        return repo_type(conn)

    return func
