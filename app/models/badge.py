from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from dictionaries import DietType
from dictionaries.dictionaries import BadgeColor, ParticipationRole
from pydantic import Field, computed_field, field_validator, model_validator

from app.dto.badge import Infant
from app.dto.direction import DirectionDTO
from app.models.base import DomainModel
from app.models.person import Person


class Badge(DomainModel):
    name: str
    last_name: str | None = None
    first_name: str | None = None
    nickname: str | None = None
    gender: str | None = None
    phone: str | None = None
    infant: Infant | UUID | None = None
    diet: DietType = Field(default_factory=DietType.default)
    feed: str | None = None
    number: str
    batch: int
    role: ParticipationRole
    photo: str | None = None
    person: Person | UUID | None = None
    comment: str | None = None
    occupation: str = "Свои"
    notion_id: UUID | None = None

    last_updated: datetime | None = None
    directions: list[DirectionDTO] | None = Field(default_factory=list)

    @computed_field
    @property
    def color(self) -> BadgeColor:
        match self.role:
            case ParticipationRole.ORGANIZER:
                return BadgeColor.RED

            case ParticipationRole.VOLUNTEER | ParticipationRole.VICE | ParticipationRole.TEAM_LEAD:
                return BadgeColor.GREEN

            case ParticipationRole.MEDIC:
                return BadgeColor.PURPLE

            case ParticipationRole.CAMP_LEAD | ParticipationRole.CAMP_GUY:
                return BadgeColor.BLUE

            case ParticipationRole.FELLOW:
                return BadgeColor.YELLOW

            case ParticipationRole.CONTRACTOR:
                return BadgeColor.GRAY

            case _:
                return BadgeColor.ORANGE

    @staticmethod
    def get_default_file(color: BadgeColor):
        path_to_files = Path.cwd() / Path("media/image/faces_no_photo")
        return str(path_to_files / Path(f"{color.value}.png"))

    @field_validator("role", mode="before")
    @classmethod
    def convert_role(cls, value: str):
        try:
            return ParticipationRole[value]
        except KeyError:
            return value

    @field_validator("diet", mode="before")
    @classmethod
    def convert_diet(cls, value: str):
        if not value:
            return DietType.default()
        try:
            return DietType[value.lower()]
        except KeyError:
            return value.lower()

    @model_validator(mode="after")
    def set_default_photo(self) -> str:
        if not self.photo:
            self.photo = self.get_default_file(self.color)
        return self

    # @staticmethod
    # def from_feeder(actor_badge, data: BadgeAPI) -> 'Badge':
    #     return Badge(
    #         id=actor_badge,
    #         name=data.name,
    #         last_name=data.last_name,
    #         first_name=data.first_name,
    #         nickname=None,  # Assuming 'nickname' is not provided in the input data
    #         gender=Gender(data.gender) if data.gender else None,
    #         phone=data.phone,
    #         infant=None,  # TODO: уточнить что делать с этим полем, feeder присылает bool (is_infant)
    #         diet=DietType("веган") if data.vegan else DietType.default(),  # TODO: мигрировать в bool?
    #         feed=FeedType(data.feed) if data.feed else None,
    #         number=data.number,
    #         batch=0,  # TODO: уточнить что за data.batch
    #         role=ParticipationRole(data.role) if data.role else None,
    #         photo=data.photo,
    #         person=UUID(data.person) if isinstance(data.person, str) else data.person,
    #         comment=data.comment,
    #         notion_id=UUID(data.notion_id) if data.notion_id else None,
    #         last_updated=datetime.now(timezone.utc),
    #         directions=[],  # TODO: уточнить
    #     )
