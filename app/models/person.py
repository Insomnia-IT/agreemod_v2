from datetime import date
from typing import List

from dictionaries.diet_type import DietType
from dictionaries.gender import Gender
from pydantic import Field

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
