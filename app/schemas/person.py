from uuid import UUID

from pydantic import BaseModel, model_validator


class PersonFiltersDTO(BaseModel):
    telegram: str | None = None
    phone: str | None = None
    email: str | None = None
    strict: bool = False

    @model_validator(mode="after")
    def format_phone(self):
        if not self.phone or self.strict:
            return self
        self.phone = self.phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if self.phone[0] == "8":
            self.phone = "+7" + self.phone[1:]
        elif self.phone[0] == "9":
            self.phone = "+7" + self.phone
        return self

    @model_validator(mode="after")
    def format_telegram(self):
        if self.telegram and self.telegram[0] != "@" and not self.strict:
            self.telegram = "@" + self.telegram
        return self


class PersonResponseSchema(BaseModel): ...


class ParticipationShort(BaseModel):
    """Краткое представление участия человека в направлении."""

    year: int
    direction_uuid: UUID
    role: str


class TelebotResponseSchema(BaseModel):
    """
    Ответ для ботов выдачи промокодов.

    Используется в:
    - https://github.com/Insomnia-IT/promocode_bot
    - https://git.asocialpsihopat.net/samson/promocode_bot_cw
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
    participations: list[ParticipationShort] = []
