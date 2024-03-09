import datetime

from pydantic import Field

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
    diet: str | None = Field(..., alias="Питание 2023")
    comment: str | None = Field(..., alias="Коммент")

    @classmethod
    def from_notion(cls, notion_id, data: dict) -> 'Person':
        data_for_model = {}
        for key in all_keys:
            key_data = data.get(key)
            extracted = cls.process_key_data(key, key_data)
            data_for_model[key] = extracted

        return cls(**data_for_model, notion_id=notion_id)

    @classmethod
    def process_key_data(cls, key, value):
        match key:

            case "Как звать":
                return cls.extract_title(value)

            case "Фамилия":
                return cls.extract_rich_text(value)

            case "Имя":
                return cls.extract_rich_text(value)

            case "Позывной":
                return cls.extract_rich_text(value)

            case "Другие прозвища":
                return cls.extract_rich_text(value)

            case "Пол":
                return cls.extract_rich_text(value)

            case "Дата рождения":
                date_raw = value.get("date")
                if date_raw:
                    date_str = date_raw.get("start")
                    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                else:
                    date = None
                return date

            case "Город":
                return cls.extract_rich_text(value)

            case "Telegram":
                return cls.extract_rich_text_telegram(value)

            case "Телефон":
                result = value.get("phone_number", None)
                return result

            case "Email":
                result = value.get("email", None)
                return result

            case "Питание 2023":
                return cls.extract_rich_text(value)

            case "Коммент":
                return cls.extract_rich_text(value)

    @staticmethod
    def extract_rich_text(data):
        result = data.get("rich_text")
        if result:
            result = result[0].get("plain_text", None)
        else:
            result = None
        return result

    @staticmethod
    def extract_rich_text_telegram(data):
        result = data.get("rich_text")
        if result:
            result = result[0].get("plain_text", None)
            if result.startswith("@"):
                result = result[1:]
        else:
            result = None
        return result

    @staticmethod
    def extract_title(data):
        result = data.get("title")
        if result:
            result = result[0].get("plain_text", None)
        else:
            result = None
        return result

    class Config:
        extra = "ignore"
