from enum import StrEnum
from uuid import UUID

from dictionaries.dictionaries import DirectionType
from pydantic import BaseModel, Field, field_serializer


class Direction(BaseModel):
    id: str | None = None
    deleted: bool | None = None
    name: str | None = None
    first_year: int | None = None
    last_year: int | None = None
    type: str | None = None
    notion_id: str | None = None


class DirectionResponse(BaseModel):
    id: UUID #= Field(..., validation_alias="notion_id")
    deleted: bool = False
    name: str
    first_year: int | None = None
    last_year: int | None = None
    type: DirectionType | None
    nocode_int_id: int

    @staticmethod
    def get_strenum_name(strenum: type[StrEnum], value: str):  # type: ignore
        if not strenum:
            return None
        if value is None:
            return None
        return strenum(value).value

    @field_serializer("type")
    def serialize_enums(self, strenum: StrEnum, _info):
        if strenum is not None:
            return strenum.value
        else:
            return None
