from pydantic import Field

from updater.notion.models.base import NotionModel
from updater.notion.models.primitives.number import Number
from updater.notion.models.primitives.select import Select
from updater.notion.models.primitives.title import Title


class Direction(NotionModel):
    name: Title = Field(..., alias="Name")
    type: Select = Field(..., alias="Тип")
    first_year: Number = Field(..., alias="Год появления")
    last_year: Number = Field(..., alias="Последний год")
