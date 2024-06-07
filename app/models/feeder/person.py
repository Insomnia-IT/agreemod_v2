from pydantic import BaseModel


class Person(BaseModel):
    id: str | None = None
    deleted: bool | None = None
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    nickname: str | None = None
    other_names: str | None = None
    gender: str | None = None
    birth_date: str | None = None
    phone: str | None = None
    telegram: str | None = None
    email: str | None = None
    city: str | None = None
    vegan: bool | None = None
    notion_id: str | None = None
