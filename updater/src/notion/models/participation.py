from dictionaries.participation_role import ParticipationRole
from dictionaries.participation_status import ParticipationStatus
from dictionaries.participation_type import ParticipationType
from updater.src.notion.models.base import NotionModel
from updater.src.notion.models.primitives.rich_text import RichText
from updater.src.notion.models.primitives.title import Title
from updater.src.notion.models.primitives.select import Select
from updater.src.notion.models.primitives.relation import Relation
from pydantic import Field, field_validator


class Participation(NotionModel):
    # name: Title = Field(..., alias="Name") # имя в notion есть но его нет в orm
    person_id: Relation = Field(..., alias="Человек")
    year: RichText = Field(..., alias="Год")
    direction_id: Relation = Field(..., alias="Службы и локации")
    role_code: Select = Field(..., alias="Роль")

    participation_code: str = ParticipationType.FELLOW.name
    status_code: str = ParticipationStatus.PENDING.name

    @staticmethod
    def get_key_from_value(value, enum_class):
        for enum_member in enum_class:
            if enum_member.value == value:
                return enum_member.name
        return None

    @field_validator("role_code")
    @classmethod
    def role_code_convert(cls, value):
        if value.value:
            key_to_look = value.value.lower()
            participation_role = cls.get_key_from_value(key_to_look, ParticipationRole)
            return participation_role
        else:
            return ParticipationRole.OTHER.name

    @field_validator("participation_code")
    @classmethod
    def participation_code_convert(cls, value):
        if value.value:
            key_to_look = value.value.lower()
            participation_role = cls.get_key_from_value(key_to_look, ParticipationType)
            return participation_role
        else:
            return ParticipationType.FELLOW.name

    @field_validator("status_code")
    @classmethod
    def status_code_convert(cls, value):
        if value.value:
            key_to_look = value.value.lower()
            participation_role = cls.get_key_from_value(key_to_look, ParticipationStatus)
            return participation_role
        else:
            return ParticipationStatus.PENDING.name

    @field_validator("year")
    @classmethod
    def convert_year(cls, value: Title):
        if value.value:
            return int(value.value)
        else:
            return None


if __name__ == '__main__':
    volunteer_data = {
        "notion_id": "0ba630b9-0dcf-4378-8e52-fb69b827c29d",
        "Name": {"title": [{"text": {"content": " "}}]},
        "Человек": {"relation": [{"id": "02430581-346b-471a-8912-a9dcaed9732a"}]},
        "Год": {"number": 2016},
        "Службы и локации": {"relation": [{"id": "b30d44af-e187-4dd6-af88-6105b3e8afdb"}]},
        "Роль": {"select": {"name": "Волонтёр"}},
        "Тип": {"select": {"name": "Федеральная локация"}}
    }

    # Create an instance of the Volunteer model
    volunteer = Participation(**volunteer_data)
    print(volunteer_data)
