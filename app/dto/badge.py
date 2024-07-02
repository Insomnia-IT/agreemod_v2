from uuid import UUID

from dictionaries import DietType
from dictionaries.dictionaries import ParticipationRole
from pydantic import BaseModel, Field, field_validator


class BadgeDTO(BaseModel):
    id: UUID
    name: str
    last_name: str | None = None
    first_name: str | None = None
    nickname: str | None = None
    number: str
    batch: int
    role: ParticipationRole | None = None
    notion_id: UUID | None = None


class Parent(BaseModel):
    id: UUID
    name: str
    last_name: str | None = None
    first_name: str | None = None
    nickname: str | None = None
    gender: str | None = None
    phone: str | None = None
    diet: DietType | None = Field(default_factory=DietType.default)
    feed: str | None = None
    number: str
    batch: int

    @field_validator("diet", mode="before")
    @classmethod
    def convert_diet(cls, value: str):
        if not value:
            return None
        return DietType[value]
