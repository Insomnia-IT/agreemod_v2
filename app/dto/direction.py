from uuid import UUID

from dictionaries.dictionaries import DirectionType
from pydantic import BaseModel, field_validator


class DirectionDTO(BaseModel):
    id: UUID | None = None
    name: str | None = None
    type: DirectionType | None = None
    nocode_int_id: int

    @field_validator("type", mode="before")
    @classmethod
    def convert_type(cls, value: str) -> str:
        try:
            return DirectionType[value].value
        except KeyError:
            return value
