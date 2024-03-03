from typing import List
from pydantic import BaseModel, Field
from datetime import date

from app.dictionaries.diet_type import DietType


class Person(BaseModel):
    name: str
    last_name: str | None = None
    first_name: str | None = None
    nickname: str | None = None
    other_names: List[str] | None = None
    gender: str | None = None
    birth_date: date | None = None
    city: str | None = None
    telegram: str | None = None
    phone: str | None = None
    email: str | None = None
    diet: DietType = Field(default_factory=DietType.default)
    comment: str | None = None
    notion_id: str
