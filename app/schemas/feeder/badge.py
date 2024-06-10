from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from dictionaries import FeedType
from dictionaries.dictionaries import ParticipationRole


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
