from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import AnyUrl
from pydantic import BaseModel as BaseModel


class BaseNotionModel(BaseModel, ABC):
    pass

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
    content: str | int | float
    link: Link | None = None


class File(BaseModel):
    url: AnyUrl | str


class ExternalFile(BaseModel):
    url: AnyUrl


class Id(BaseModel):
    id: UUID


class User(BaseModel):
    object: str
    id: UUID


class MentionPage(BaseModel):
    type: str
    page: Id


class MentionUser(BaseModel):
    type: str
    user: User
