from datetime import date
from enum import StrEnum
from uuid import UUID

from dictionaries.diet_type import DietType
from dictionaries.gender import Gender
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class PersonResponse(BaseModel):
    id: UUID #= Field(..., validation_alias="nocode_int_id")
    deleted: bool = False
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    nickname: str | None = None
    other_names: str | None = None
    gender: Gender | None
    birth_date: date | None = None
    phone: str | None = None
    telegram: str | None = None
    email: str | None = None
    city: str | None = None
    vegan: bool = Field(..., validation_alias="diet")
    nocode_int_id: int

    model_config = ConfigDict(
        json_encoders={
            Gender: lambda g: g.name,
        }
    )

    @field_serializer("gender")
    def serialize_enums(self, strenum: StrEnum, _info):
        if not strenum:
            return None
        return strenum.name

    @field_validator("other_names", mode="before")
    def convert_to_str(cls, values: list[str]):
        return ", ".join(values)

    @field_validator("vegan", mode="before")
    def convert_non_vegan(cls, value: bool):
        if not value or value == DietType.STANDARD.value:
            return False
        else:
            return True
