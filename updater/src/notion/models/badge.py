from uuid import UUID

import psycopg2

from dictionaries.dictionaries import BadgeColor, ParticipationRole
from dictionaries.diet_type import DietType
from dictionaries.feed_type import FeedType
from dictionaries.gender import Gender
from pydantic import Field, field_validator, model_validator
from updater.src.config import config
from updater.src.notion.models.base import NotionModel
from updater.src.notion.models.primitives.checkbox import Checkbox
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
    parent_id: Relation = Field(..., alias="Чей")
    child: Checkbox = Field(..., alias="Ребенок")
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
        try:
            conn = psycopg2.connect(
                database=config.postgres.name,
                user=config.postgres.user,
                password=config.postgres.password,
                host=config.postgres.host,
                port=config.postgres.port,
            )
            cur = conn.cursor()
            cur.execute("SELECT name, number, notion_id FROM public.badge")
            badges = cur.fetchall()
        finally:
            conn.close()
        exist = next(
            (
                number
                for name, number, notion_id in badges
                if str(notion_id) == str(self.notion_id)
            ),
            None,
        )
        if exist:
            self.number = exist
            return self
        direction_num: int = (
            self.direction_id_.value[0].int % 1000 if self.direction_id_.value else 0
        )
        personal_num = (
            max(
                [
                    int(number.split("-")[-1])
                    for name, number, notion_id in badges
                    if number
                    and int(number.split("-")[0]) == direction_num
                ],
                default=0,
            )
            + 1
        )
        self.number = f"{direction_num:03}-{personal_num:03}"
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
        elif value.select.name.lower() in ["другой", "other"]:
            gender = cls.get_key_from_value("другой", Gender)
        else:
            return None
        return gender

    @field_validator("diet", mode="after")
    @classmethod
    def format_diet(cls, value: Select):
        if not value.select:
            return None
        diet = cls.get_key_from_value(value.select.name.lower(), DietType)
        return diet

    @field_validator("feed", mode="after")
    @classmethod
    def format_feed(cls, value: Select):
        if not value.select:
            return None
        feed = cls.get_key_from_value(value.select.name, FeedType)
        return feed

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
        "parent_id",
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


class Anons(NotionModel):
    title: Title = Field(..., alias="Основная надпись")
    subtitle: RichText = Field(..., alias="Дополнительная надпись")
    batch: Select = Field(..., alias="Партия")
    color: Select = Field(..., alias="Цвет")
    quantity: Number = Field(..., alias="Количество")
    to_print: Checkbox = Field(..., alias="QR")

    @staticmethod
    def get_key_from_value(value, enum_class):
        for enum_member in enum_class:
            if enum_member.value == value:
                return enum_member.name
        return None

    @field_validator("color", mode="after")
    @classmethod
    def convert_color(cls, value):
        if value.value:
            return cls.get_key_from_value(
                value.value.replace("ё", "е").lower(), BadgeColor
            )
        else:
            return None
