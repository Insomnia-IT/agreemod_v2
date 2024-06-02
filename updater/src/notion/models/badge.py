import hashlib

from uuid import UUID

import psycopg2

from dictionaries.dictionaries import ParticipationRole
from dictionaries.gender import Gender
from pydantic import Field, field_validator, model_validator
from updater.src.config import config
from updater.src.notion.models.base import NotionModel
from updater.src.notion.models.primitives.files import Files
from updater.src.notion.models.primitives.number import Number
from updater.src.notion.models.primitives.relation import Relation
from updater.src.notion.models.primitives.rich_text import RichText
from updater.src.notion.models.primitives.select import Select
from updater.src.notion.models.primitives.title import Title


class Badge(NotionModel):
    name: Title = Field(..., alias="Надпись")
    last_name: RichText = Field(..., alias="Фамилия")
    first_name: RichText = Field(..., alias="Имя")
    nickname: Title = Field(..., alias="Надпись")
    gender: Select = Field(..., alias="Пол")
    phone: RichText = Field(..., alias="Телефон")
    infant_id: Relation = Field(..., alias="Чей")
    diet: Select = Field(..., alias="Особенности питания")
    feed: Select = Field(..., alias="Тип питания")
    number: RichText = Field(..., alias="Номер")
    batch: Select = Field(..., alias="Партия")
    # participation_code: Relation = Field(..., alias='Роль')
    occupation: RichText = Field(..., alias="Должность")
    role_code: Relation = Field(..., alias="Роль")
    photo: Files = Field(..., alias="Фото")
    person_id: Relation = Field(..., alias="Человек")
    comment: RichText = Field(..., alias="Комментарий")
    direction_id_: Relation = Field(..., alias="Службы и локации")

    @staticmethod
    def get_key_from_value(value, enum_class):
        for enum_member in enum_class:
            if enum_member.value == value:
                return enum_member.name
        return None

    @model_validator(mode="after")
    def generate_number(self):
        if self.number.value:
            return self
        role_num: int = next(
            i for i, x in enumerate(ParticipationRole) if self.role_code == x.name
        )
        direction_num: int = (
            self.direction_id_.value[0].int % 1000 if self.direction_id_.value else 0
        )
        if self.person_id:
            personal_num: int = self.person_id.int % 10000
        else:
            h = hashlib.sha1()
            h.update(bytes(self.name, encoding="utf-8"))
            personal_num = int(h.hexdigest(), 16) % 10000

        self.number = f"{role_num:03}-{direction_num:03}-{personal_num:04}"
        return self

    @field_validator("role_code", mode="after")
    @classmethod
    def role_code_convert(cls, value: Relation):
        try:
            conn = psycopg2.connect(
                database=config.postgres.name,
                user=config.postgres.user,
                password=config.postgres.password,
                host=config.postgres.host,
                port=config.postgres.port,
            )
            cur = conn.cursor()
            cur.execute("SELECT code, notion_id FROM public.participation_role")
            roles = cur.fetchall()
        finally:
            conn.close()
        if value.value:
            notion_id_to_look = value.value[0]
            participation_role = next(
                (
                    code
                    for code, notion_id in roles
                    if UUID(notion_id) == notion_id_to_look
                ),
                ParticipationRole.FELLOW.name,
            )
            return participation_role
        else:
            return ParticipationRole.FELLOW.name

    @field_validator("phone", mode="after")
    @classmethod
    def format_phone(cls, value: RichText):
        if not value.value:
            return value
        format_value = (
            value.value.replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )
        if format_value[0] == "8":
            format_value = "+7" + format_value[1:]
        elif format_value[0] == "9":
            format_value = "+7" + format_value
        elif format_value[0] == "7":
            format_value = "+" + format_value
        return format_value

    @field_validator("gender", mode="after")
    @classmethod
    def format_gender(cls, value: Select):
        if not value.select:
            return None
        if value.select.name.lower() in ["ж", "женский", "f", "female"]:
            gender = cls.get_key_from_value("женский", Gender)
        elif value.select.name.lower() in ["м", "мужской", "m", "male"]:
            gender = cls.get_key_from_value("мужской", Gender)
        else:
            return None
        return gender

    @field_validator(
        "name",
        "last_name",
        "first_name",
        "nickname",
        "occupation",
        mode="after",
    )
    @classmethod
    def strip_spaces_rc(cls, value: RichText | Title):
        result = value.value.strip()
        return result

    @field_validator(
        "infant_id",
        "person_id",
        mode="after",
    )
    @classmethod
    def get_relation(cls, value: Relation):
        if not value.value:
            return None
        return value.value[0]

    @field_validator("photo", mode="after")
    @classmethod
    def get_photo(cls, value: Files):
        return str(value.url) if value.url else None

    @field_validator("batch", mode="after")
    @classmethod
    def set_batch(cls, value: Number):
        if value.value:
            return int(value.value)
        else:
            return 1