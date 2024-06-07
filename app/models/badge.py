from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from app.models.feeder.badge import Badge as BadgeAPI

from dictionaries import DietType, FeedType, Gender
from dictionaries.dictionaries import BadgeColor, ParticipationRole
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
    role: ParticipationRole | None
    photo: str | None = None
    person: Person | UUID | None = None
    comment: str | None = None
    notion_id: UUID | None = None

    last_updated: datetime | None = None
    directions: list[DirectionDTO] = Field(default_factory=list)

    # TODO: проверить нужен ли этот метод, participation атрибута нету
    # @computed_field
    # @property
    # def color(self) -> BadgeColor:
    #     return self.participation.badge_color

    @staticmethod
    def get_default_file(color: BadgeColor):
        path_to_files = Path.cwd() / Path("media/image/faces_no_photo")
        return path_to_files / Path(f"{color.value}.png")

    # TODO: проверить нужен ли этот метод, приводит к ошибке при синхронизации в feeder
    # TODO: AttributeError: 'Badge' object has no attribute 'color'
    # @model_validator(mode="after")
    # def set_default_photo(self) -> str:
    #     if not self.photo:
    #         self.photo = self.get_default_file(self.color)
    #     return self

    @staticmethod
    def from_feeder(actor_badge, data: 'BadgeAPI') -> 'Badge':
        return Badge(
            id=actor_badge,
            name=data.name,
            last_name=data.last_name,
            first_name=data.first_name,
            nickname=None,  # Assuming 'nickname' is not provided in the input data
            gender=Gender(data.gender) if data.gender else None,
            phone=data.phone,
            infant=None,  # TODO: уточнить что делать с этим полем, feeder присылает bool (is_infant)
            diet=DietType("веган") if data.vegan else DietType.default(),  # TODO: мигрировать в bool?
            feed=FeedType(data.feed) if data.feed else None,
            number=data.number,
            batch=0,  # TODO: уточнить что за data.batch
            role=ParticipationRole(data.role) if data.role else None,
            photo=data.photo,
            person=UUID(data.person) if isinstance(data.person, str) else data.person,
            comment=data.comment,
            notion_id=UUID(data.notion_id) if data.notion_id else None,
            last_updated=datetime.now(timezone.utc),
            directions=[],  # TODO: уточнить
        )
