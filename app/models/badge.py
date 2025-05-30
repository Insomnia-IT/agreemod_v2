from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from dictionaries import DietType
from dictionaries.dictionaries import BadgeColor, ParticipationRole
from dictionaries.gender import Gender
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer, field_validator, model_validator

from app.dto.badge import Parent
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
    parent: Parent | int | UUID | None = None
    child: bool | None = False
    diet: DietType = Field(default_factory=DietType.default)
    feed: str | None = None
    number: str | None = None
    batch: int | None = None
    role: ParticipationRole
    photo: str | None = None
    person: Person | int | UUID | None = None
    comment: str | None = None
    occupation: str
    nocode_int_id: int | None = None
    deleted: bool | None = False

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

    model_config = ConfigDict(
        json_encoders={
            DietType: lambda t: t.name,
            ParticipationRole: lambda p: p.name,
            Gender: lambda g: g.name,
        },
        use_enum_values=False,
    )

    @field_serializer("batch")
    def serialize_batch(self, value, _info):
        return str(value) if value else None

    @staticmethod
    def get_default_file(color: BadgeColor):
        path_to_files = Path.cwd() / Path("media/image/faces_no_photo")
        return str(path_to_files / Path(f"{color.value}.png"))

    @field_validator("batch", mode="before")
    @classmethod
    def convert_batch(cls, value):
        if value == 'None' or value is None:
            return None
        else:
            return int(value)

    @field_validator("role", mode="before")
    @classmethod
    def convert_role(cls, value: str):
        try:
            return ParticipationRole[value]
        except KeyError:
            return value

    @field_validator("gender", mode="before")
    @classmethod
    def convert_gender(cls, value: str):
        if value == '':
            return None
        try:
            return Gender[value]
        except KeyError:
            if value == 'М':
                return Gender.MALE
            elif value == 'Ж':
                return Gender.FEMALE
            elif value == 'др.':
                return Gender.OTHER
            else:
                return value

    @field_validator("diet", mode="before")
    @classmethod
    def convert_diet(cls, value: str):
        if not value:
            return DietType.default()
        try:
            return DietType(value.lower())
        except ValueError:
            return DietType.default()

    @model_validator(mode="after")
    def set_default_photo(self) -> str:
        if not self.photo:
            self.photo = self.get_default_file(self.color)
        return self

    @model_validator(mode="before")
    @classmethod
    def set_empty_occupation(cl, data: Any):
        if not data.get("occupation"):
            data["occupation"] = data["role"]
        return data


class Anons(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    batch: str
    color: str | None = None
    quantity: int = 0
    to_print: bool

    @field_validator("quantity", mode="before")
    @classmethod
    def set_quantity(cls, value) -> int:
        if not value:
            return 0
        return value
