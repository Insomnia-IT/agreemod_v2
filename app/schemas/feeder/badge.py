from __future__ import annotations

from datetime import datetime
from uuid import UUID

from dictionaries import FeedType
from dictionaries.dictionaries import ParticipationRole
from pydantic import BaseModel, Field


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

    @staticmethod
    def from_db(badge: "Badge") -> Badge:
        return Badge(
            id=str(badge.id) if badge.id else None,
            deleted=False,  # TODO: доработать этот функционал
            name=badge.name,
            first_name=badge.first_name,
            last_name=badge.last_name,
            nickname=badge.nickname,
            gender=badge.gender,
            phone=badge.phone,
            infant=badge.infant,
            diet=badge.diet,
            feed=badge.feed,
            number=badge.number,
            batch=str(badge.batch),
            role=badge.role,
            photo=badge.photo,
            person=str(badge.person) if badge.person else None,
            comment=badge.comment,
            notion_id=str(badge.notion_id) if badge.notion_id else None,
            last_updated=badge.last_updated,
            directions=badge.directions,
        )


class BadgeWithMetadata(BaseModel):
    actor_badge: UUID | None = None
    date: datetime | None = None
    data: Badge | None = None
