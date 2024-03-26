from typing import Literal

from dictionaries.diet_type import DietType
from pydantic import ConfigDict, Field, field_validator, model_validator
from updater.notion.models.base import NotionModel
from updater.notion.models.primitives.checkbox import Checkbox
from updater.notion.models.primitives.date import Date
from updater.notion.models.primitives.email import Email
from updater.notion.models.primitives.phone_number import PhoneNumber
from updater.notion.models.primitives.rich_text import RichText
from updater.notion.models.primitives.select import Select
from updater.notion.models.primitives.title import Title


all_keys = [
    "Как звать",
    "Фамилия",
    "Имя",
    "Позывной",
    "Другие прозвища",
    "Пол",
    "Дата рождения",
    "Город",
    "Telegram",
    "Телефон",
    "Email",
    "Питание 2023",
    "Коммент",
]


class Person(NotionModel):
    model_config = ConfigDict(extra="ignore")

    name: Title = Field(..., alias="Как звать")
    last_name: RichText | None = Field(..., alias="Фамилия")
    first_name: RichText | None = Field(..., alias="Имя")
    nickname: RichText | None = Field(..., alias="Позывной")
    other_names: RichText | list[str] | None = Field(..., alias="Другие прозвища")
    gender: Select | None = Field(..., alias="Пол")
    birth_date: Date | None = Field(..., alias="Дата рождения")
    city: Select | None = Field(..., alias="Город")
    telegram: RichText | None = Field(..., alias="Telegram")
    phone: PhoneNumber | None = Field(..., alias="Телефон")
    email: Email | None = Field(..., alias="Email")
    diet: Literal["с мясом", "без мяса"] = "с мясом"
    comment: RichText | None = Field(..., alias="Коммент")
    is_vegan_: Checkbox = Field(..., alias="Веган")

    @field_validator("name")
    @classmethod
    def name_strip_spaces(cls, value: Title):
        for t in value.title:
            t.plain_text = t.plain_text.strip()
        return value

    @field_validator("phone")
    @classmethod
    def format_phone(cls, value: PhoneNumber):
        if not value.phone_number:
            return value
        value.phone_number = (
            value.phone_number.replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )
        if value.phone_number[0] == "8":
            value.phone_number = "+7" + value.phone_number[1:]
        elif value.phone_number[0] == "9":
            value.phone_number = "+7" + value.phone_number
        return value

    @field_validator("gender")
    @classmethod
    def format_gender(cls, value: Select):
        if value.select:
            if value.select.name.lower() in ["ж", "женский", "f", "female"]:
                value.select.name = "женский"
            elif value.select.name.lower() in ["м", "мужской", "m", "male"]:
                value.select.name = "мужской"
        return value

    @field_validator("telegram")
    @classmethod
    def format_telegram(cls, value: RichText):
        for t in value.rich_text:
            if t.plain_text and t.plain_text[0] != "@":
                t.plain_text = "@" + t.plain_text
        return value

    @field_validator("other_names")
    @classmethod
    def format_other_names(cls, value: RichText):
        result = [t.plain_text for t in value.rich_text]
        return result

    @model_validator(mode="after")
    def is_vegan(self):
        if self.is_vegan_.checkbox is True:
            self.diet = DietType.VEGAN
        else:
            self.diet = DietType.default()
        return self
