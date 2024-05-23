from pydantic import BaseModel

class Person(BaseModel):
    id: str
    deleted: bool
    name: str
    first_name: str
    last_name: str
    nickname: str
    other_names: str
    gender: str
    birth_date: str
    phone: str
    telegram: str
    email: str
    city: str
    vegan: bool
    notion_id: str