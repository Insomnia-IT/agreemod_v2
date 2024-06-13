from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from dictionaries import FeedType
from dictionaries.dictionaries import ParticipationRole
from dictionaries.gender import Gender
from pydantic import BaseModel, Field, field_serializer, field_validator


class Badge(BaseModel):
    id: str | None = None
    deleted: bool | None = None
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    gender: str | None = None
    phone: str | None = None
    infant: bool | None = None
    vegan: bool | None = None
    feed: FeedType | None = None
    number: str | None = None
    batch: int | None = None
    role: ParticipationRole | None = None
    position: str | None = None
    photo: str | None = None
    person: str | None = None
    comment: str | None = None
    notion_id: str | None = None
    directions: list[UUID] = Field(default_factory=list)


class BadgeWithMetadata(BaseModel):
    actor_badge: UUID | None = None
    date: datetime | None = None
    data: Badge | None = None


class BadgeResponse(BaseModel):
    id: UUID
    deleted: bool = False
    name: str
    first_name: str
    last_name: str
    gender: Gender | None
    phone: str
    infant: bool
    vegan: bool = Field(..., validation_alias="diet")
    feed: FeedType = Field(FeedType.NO)
    number: str
    batch: str
    role: ParticipationRole
    position: str = Field(..., validation_alias="occupation")
    photo: str
    person: UUID | None
    comment: str
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
        return value

    @field_validator("directions", mode="before")
    @classmethod
    def list_directions(cls, values: list[dict]) -> list[str]:
        return [x['notion_id'] for x in values]