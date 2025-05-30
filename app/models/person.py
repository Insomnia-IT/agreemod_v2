from datetime import date, datetime
from typing import List
from uuid import UUID

from dictionaries.diet_type import DietType
from dictionaries.gender import Gender
from pydantic import Field, field_validator

from app.models.base import DomainModel


class Person(DomainModel):
    name: str
    last_name: str | None = None
    first_name: str | None = None
    nickname: str | None = None
    other_names: List[str] | None = None
    gender: Gender | None = None
    birth_date: date | None = None
    city: str | None = None
    telegram: str | None = None
    phone: str | None = None
    email: str | None = None
    diet: DietType | None = Field(default_factory=DietType.default)
    comment: str | None = None
    nocode_int_id: int | None = None
    last_updated: datetime | None = None
    deleted: bool | None = False

    @field_validator("gender", mode="before")
    def convert_gender(cls, value: str):
        if value == '':
            return None
        try:
            return Gender[value]
        except KeyError:
            return value
