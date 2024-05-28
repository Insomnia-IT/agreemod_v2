from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Badge(BaseModel):
    id: str
    deleted: bool
    name: str
    first_name: str
    last_name: str
    gender: str
    phone: str
    infant: bool
    vegan: bool
    feed: str
    number: str
    batch: str
    role: str
    position: str
    photo: str
    person: str
    comment: str
    notion_id: str


class BadgeWithMetadata(BaseModel):
    actor_badge: UUID
    date: datetime
    data: Badge
