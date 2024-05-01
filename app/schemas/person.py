from uuid import UUID

from pydantic import BaseModel


class PersonFiltersDTO(BaseModel):
    telegram: str
    phone_number: str
    email: str


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
