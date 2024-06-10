from pydantic import BaseModel

from dictionaries import DietType


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

    @staticmethod
    def from_db(person: 'Person') -> 'Person':
        return Person(
            id=str(person.id) if person.id else None,
            name=person.name,
            first_name=person.first_name,
            last_name=person.last_name,
            nickname=person.nickname,
            other_names=', '.join(person.other_names) if person.other_names else None,
            gender=person.gender,
            birth_date=str(person.birth_date) if person.birth_date else None,
            phone=person.phone,
            telegram=person.telegram,
            email=person.email,
            city=person.city,
            vegan=person.diet == DietType.VEGAN if person.diet else None,
            notion_id=str(person.notion_id) if person.notion_id else None
        )
