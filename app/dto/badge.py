from uuid import UUID

from pydantic import BaseModel, Field
from dictionaries import (
    DietType,
    FeedType,
    Gender,
    ParticipationRole,
    ParticipationType,
)


class BadgeDTO(BaseModel):
    id: UUID
    name: str
    last_name: str | None = None
    first_name: str | None = None
    nickname: str | None = None
    number: str
    batch: int
    role: ParticipationRole | None
    participation: ParticipationType
    notion_id: UUID | None = None


class Infant(BaseModel):
    id: UUID
    name: str
    last_name: str | None = None
    first_name: str | None = None
    nickname: str | None = None
    gender: Gender | None = None
    phone: str | None = None
    diet: DietType = Field(default_factory=DietType.default)
    feed: FeedType | None = None
    number: str
    batch: int
