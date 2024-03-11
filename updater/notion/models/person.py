import datetime

from pydantic import ConfigDict, Field, field_validator

from app.dictionaries.diet_type import DietType
from updater.notion.models.base import NotionModel


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

    name: str | None = Field(..., alias="Как звать")
    last_name: str | None = Field(..., alias="Фамилия")
    first_name: str | None = Field(..., alias="Имя")
    nickname: str | None = Field(..., alias="Позывной")
    other_names: str | None = Field(..., alias="Другие прозвища")
    gender: str | None = Field(..., alias="Пол")
    birth_date: datetime.date | None = Field(..., alias="Дата рождения")
    city: str | None = Field(..., alias="Город")
    telegram: str | None = Field(..., alias="Telegram")
    phone: str | None = Field(..., alias="Телефон")
    email: str | None = Field(..., alias="Email")
    diet: DietType = Field(DietType.default, alias="Питание 2023")
    comment: str | None = Field(..., alias="Коммент")

    @field_validator("*", mode="before", check_fields=False)
    @classmethod
    def process_key_data(cls, v, field):
        field_name = field.field_name

        if field_name == "notion_id":
            return v

        if field_name == "name":
            return cls.extract_title(v)

        if field_name == "birth_date":
            date_raw = v.get("date")
            date_str = date_raw.get("start") if date_raw else None
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None

        if field_name == "telegram":
            return cls.extract_rich_text_telegram(v)

        if field_name == "diet":
            if isinstance(v, str):
                if v.lower() == "с мясом":
                    return DietType.STANDARD.value
                elif v.lower() == "без мяса":
                    return DietType.VEGAN.value
            else:
                return DietType.STANDARD.value

        return cls.extract_rich_text(v)

    @staticmethod
    def extract_rich_text(data):
        result = data.get("rich_text")
        return result[0].get("plain_text") if result else None

    @staticmethod
    def extract_rich_text_telegram(data):
        result = data.get("rich_text")
        if result:
            result = result[0].get("plain_text")
            if result.startswith("@"):
                result = result[1:]
            return result
        return None

    @staticmethod
    def extract_title(data):
        result = data.get("title")
        if result:
            result = result[0].get("plain_text", None)
        else:
            result = None
        return result
