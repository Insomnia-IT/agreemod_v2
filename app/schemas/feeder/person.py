from datetime import datetime
from enum import StrEnum
from uuid import UUID

from dictionaries.gender import Gender
from pydantic import BaseModel, ConfigDict, field_serializer, field_validator


class PersonResponse(BaseModel):
    id: UUID
    deleted: bool = False
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    nickname: str | None = None
    other_names: str | None = None
    gender: Gender | None
    birth_date: datetime | None = None
    phone: str | None = None
    telegram: str | None = None
    email: str | None = None
    city: str | None = None
    vegan: bool | None = None
    notion_id: UUID

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
    def conver_to_str(cls, values: list[str]):
        return ", ".join(values)
