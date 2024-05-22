from uuid import UUID

from pydantic import BaseModel, field_validator


class PersonFiltersDTO(BaseModel):
    telegram: str | None = None
    phone_number: str | None = None
    email: str | None = None

    @field_validator("phone")
    @classmethod
    def format_phone(cls, value: str):
        if not value:
            return value
        value = (
            value.replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )
        if value[0] == "8":
            value = "+7" + value[1:]
        elif value[0] == "9":
            value = "+7" + value
        return value

    @field_validator("telegram")
    @classmethod
    def format_telegram(cls, value: str):
        if value and value[0] != "@":
            value = "@" + value
        return value



class PersonResponseSchema(BaseModel): ...


class TelebotResponseSchema(BaseModel):
    """
    модель скопирована из https://github.com/Insomnia-IT/promocode_bot
    бот ожидает получить пользователя в таком виде
    """

    uuid: UUID
    nickname: str
    lastname: str
    name: str

    telegram: str | None
    email: str | None
    second_email: str | None
    phone_number: str | None

    role: str | None

    volunteer: list[str]
    organize: list[str]
