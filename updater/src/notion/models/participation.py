from dictionaries.dictionaries import (
    ParticipationRole,
    ParticipationStatus,
)
from pydantic import Field, field_validator
from updater.src.notion.models.base import NotionModel
from updater.src.notion.models.primitives.relation import Relation
from updater.src.notion.models.primitives.rich_text import RichText
from updater.src.notion.models.primitives.select import Select
from updater.src.notion.models.primitives.title import Title


class Participation(NotionModel):
    # name: Title = Field(..., alias="Name") # имя в notion есть но его нет в orm
    person_id: Relation = Field(..., alias="Человек")
    year: RichText = Field(..., alias="Год")
    direction_id: Relation = Field(..., alias="Службы и локации")
    role_code: Select = Field(..., alias="Роль")
    status_code: Select = Field(..., alias="Статус")

    @staticmethod
    def get_key_from_value(value, enum_class):
        for enum_member in enum_class:
            if enum_member.value == value:
                return enum_member.name
        return None

    @field_validator("role_code", mode="before")
    @classmethod
    def role_code_prepare(cls, value: Select):
        if value.value == 'Зам.руководителя':
            value.value = 'Зам. руководителя'
        elif value.value == 'Свои (плюсодин)':
            value.value = 'Свои (плюсодины)'
        return value

    @field_validator("role_code", mode="after")
    @classmethod
    def role_code_convert(cls, value: Select):
        if value.value:
            key_to_look = value.value.lower()
            participation_role = cls.get_key_from_value(key_to_look, ParticipationRole)
            return participation_role
        else:
            return ParticipationRole.OTHER.name

    @field_validator("status_code", mode="after")
    @classmethod
    def status_code_convert(cls, value: Select):
        if value.value:
            key_to_look = value.value.lower()
            participation_role = cls.get_key_from_value(
                key_to_look, ParticipationStatus
            )
            return participation_role
        else:
            return ParticipationStatus.PENDING.name

    @field_validator("year", mode="after")
    @classmethod
    def convert_year(cls, value: Title):
        if value.value:
            return int(value.value)
        else:
            return None

    @classmethod
    def create_model(cls, values: dict):
        model_dict = {}
        for x, y in values.items():
            print(x, y)
            if cls.model_fields.get(x):
                field = cls.model_fields[x]
                if cls.model_fields[x].annotation in [Relation, RichText]:
                    model_dict[field.alias if field.alias else x] = (
                        field.annotation.create_model([y])
                    )
                elif field.annotation in [Select]:
                    model_dict[field.alias if field.alias else x] = (
                        field.annotation.create_model(y)
                    )
                else:
                    model_dict[field.alias if field.alias else x] = y
        return cls.model_validate(model_dict)


if __name__ == "__main__":
    volunteer_data = {
        "notion_id": "0ba630b9-0dcf-4378-8e52-fb69b827c29d",
        "Name": {"title": [{"text": {"content": " "}}]},
        "Человек": {"relation": [{"id": "02430581-346b-471a-8912-a9dcaed9732a"}]},
        "Год": {"number": 2016},
        "Службы и локации": {
            "relation": [{"id": "b30d44af-e187-4dd6-af88-6105b3e8afdb"}]
        },
        "Роль": {"select": {"name": "Волонтёр"}},
        "Тип": {"select": {"name": "Федеральная локация"}},
    }

    # Create an instance of the Volunteer model
    volunteer = Participation(**volunteer_data)
    print(volunteer_data)
