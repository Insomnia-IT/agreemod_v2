from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from dictionaries import FeedType
from dictionaries.dictionaries import ParticipationRole
from dictionaries.diet_type import DietType
from dictionaries.gender import Gender
from pydantic import BaseModel, Field, field_serializer, field_validator, model_validator


class Badge(BaseModel):
    id: str | None = None
    deleted: bool | None = None
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    nickname: str = None
    gender: Gender | None = None
    phone: str | None = None
    infant: None = Field(None)
    diet: DietType | None = Field(None, validation_alias="vegan")
    feed: FeedType | None = None
    number: str | None = None
    batch: int | None = None
    role: ParticipationRole | None = None
    occupation: str | None = Field(None, validation_alias="position")
    photo: str | None = None
    person: str | None = None
    comment: str | None = None
    notion_id: str | None = None
    directions: list[UUID] = Field(default_factory=list)

    @field_validator("infant", mode="before")
    @classmethod
    def convert_infant(cls, value: str):
        return None

    @field_validator("gender", mode="before")
    @classmethod
    def convert_gender(cls, value: str):
        if not value:
            return None
        return Gender[value].value

    @field_validator("feed", mode="before")
    @classmethod
    def convert_feed(cls, value: str):
        if not value:
            return FeedType.NO.value
        return FeedType[value].value

    @field_validator("role", mode="before")
    @classmethod
    def convert_role(cls, value: str):
        return ParticipationRole[value].value

    @field_validator("diet", mode="before")
    @classmethod
    def convert_vegan(cls, value: str):
        return DietType.VEGAN.value if value is True else DietType.STANDARD.value

    # necessary evil
    @model_validator(mode="after")
    def fill_notion_id_if_none(self):
        if self.notion_id is None:
            self.notion_id = self.id
        return self


class BadgeWithMetadata(BaseModel):
    actor_badge: UUID | None = None
    date: datetime | None = None
    data: Badge | None = None


class BadgeResponse(BaseModel):
    id: UUID = Field(..., validation_alias="notion_id")
    deleted: bool = False
    name: str = ""
    first_name: str = ""
    last_name: str = ""
    gender: Gender | None
    phone: str = ""
    infant: bool
    vegan: bool = Field(..., validation_alias="diet")
    feed: FeedType = Field(FeedType.NO)
    number: str | None
    batch: str | None
    role: ParticipationRole
    position: str = Field(..., validation_alias="occupation")
    photo: str
    person: UUID | None
    comment: str | None
    notion_id: UUID
    directions: list[UUID] = Field(..., default_factory=list)

    @staticmethod
    def get_strenum_name(strenum: type[StrEnum], value: str):
        return strenum(value).name

    @field_serializer("role", "feed", "gender")
    def serialize_enums(self, strenum: StrEnum, _info):
        if not strenum:
            return None
        return strenum.name

    @field_validator("vegan", mode="before")
    @classmethod
    def convert_vegan(cls, value: str):
        if value == "VEGAN":
            return True
        return False

    @field_validator("feed", mode="before")
    @classmethod
    def validate_feed(cls, value: str) -> str:
        if not value:
            return FeedType.NO
        try:
            return FeedType(value)
        except ValueError:
            return FeedType[value]

    @field_validator("directions", mode="before")
    @classmethod
    def list_directions(cls, values: list[dict]) -> list[str]:
        return [x["notion_id"] for x in values]

    @field_validator("name", "first_name", "last_name", "phone", mode="before")
    @classmethod
    def format_str(cls, value):
        if value:
            return value
        return ""
