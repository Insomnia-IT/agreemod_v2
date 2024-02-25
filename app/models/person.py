from typing import Optional, List
from pydantic import BaseModel
from datetime import date


class Person(BaseModel):
    name: str
    last_name: Optional[str]
    first_name: Optional[str]
    nickname: Optional[str]
    other_names: Optional[List[str]]
    gender: Optional[str]
    birth_date: Optional[date]
    city: Optional[str]
    telegram: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    diet: Optional[str]
    comment: Optional[str]
    notion_id: str

    class Config:
        orm_mode = True
