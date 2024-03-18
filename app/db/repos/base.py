import logging

from typing import Any, Generic, Protocol, Type, TypeVar, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


_logger = logging.getLogger(__name__)


class _Model(Protocol):
    id: Any


TModel = TypeVar("TModel", bound=Union[DeclarativeBase, _Model])


class BaseSqlaRepo(Generic[TModel]):
    __model__: Type[TModel]

    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__()
