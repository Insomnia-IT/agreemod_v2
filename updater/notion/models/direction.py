import logging

from dictionaries.direction_type import DirectionType
from pydantic import Field, model_validator
from updater.notion.models.base import NotionModel
from updater.notion.models.primitives.number import Number
from updater.notion.models.primitives.select import Select
from updater.notion.models.primitives.title import Title


class Direction(NotionModel):
    name: Title = Field(..., alias="Name")
    type: str | None = None
    first_year: Number = Field(..., alias="Год появления")
    last_year: Number = Field(..., alias="Последний год")
    type_: Select = Field(..., alias="Тип")

    @model_validator(mode="after")
    def set_type(self):
        try:
            self.type = DirectionType(self.type_.value).name
        except ValueError:
            logging.error(
                f"Тип направления ({self.type_.value}) не соответствует ни одному известному"
            )
        return self
