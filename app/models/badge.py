from datetime import datetime
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
