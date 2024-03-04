from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import AnyUrl
from pydantic import BaseModel as BaseModel


class BaseNotionModel(BaseModel, ABC):
    id: str
    type: str

    @property
    @abstractmethod
    def value(self) -> Any: ...


class Annotations(BaseModel):
    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: str


class Link(BaseModel):
    url: str


class Text(BaseModel):
    content: str
    link: Link | None


class File(BaseModel):
    url: AnyUrl
    expiry_time: datetime | None


class ExternalFile(BaseModel):
    url: AnyUrl
