from datetime import datetime
from uuid import UUID

from dictionaries import (
    BadgeColor,
    DietType,
    FeedType,
    Gender,
    ParticipationRole,
    ParticipationType,
)
from pydantic import Field, computed_field, model_validator

from app.dto.badge import Infant
from app.dto.direction import DirectionDTO
from app.models.base import DomainModel
from app.models.person import Person


class Badge(DomainModel):
    name: str
    last_name: str | None = None
    first_name: str | None = None
    nickname: str | None = None
    gender: Gender | None = None
    phone: str | None = None
    infant: Infant | UUID | None = None
    diet: DietType = Field(default_factory=DietType.default)
    feed: FeedType | None = None
    number: str
    batch: int
    participation: ParticipationType
    role: ParticipationRole | None
    photo: str | None = None
    person: Person | UUID | None = None
    comment: str | None = None
    notion_id: UUID | None = None

    last_updated: datetime | None = None
    directions: list[DirectionDTO] = Field(default_factory=list)

    @computed_field
    @property
    def color(self) -> BadgeColor:
        return self.participation.badge_color

    @model_validator(mode="after")
    def set_default_photo(self) -> str:
        if not self.photo:
            self.photo = self.color.get_default_file()
        return self
