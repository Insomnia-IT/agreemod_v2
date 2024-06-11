from datetime import datetime
from enum import StrEnum
from uuid import UUID

from dictionaries.dictionaries import ParticipationRole, ParticipationStatus
from pydantic import BaseModel, Field, field_serializer, field_validator


class CodaParticipation(BaseModel):
    coda_index: int = Field(..., alias="id")
    year: int = Field(..., alias="Год")
    person_id: UUID = Field(..., alias="person_id")
    direction_id: UUID = Field(..., alias="direction_id")
    role_code: ParticipationRole = Field(..., alias="Роль")
    status_code: ParticipationStatus = Field(..., alias="Статус")
    notion_id: UUID | None = None
    last_updated: datetime = Field(default_factory=datetime.now)

    @field_validator("year")
    @classmethod
    def filter_year(cls, value: int) -> int:
        assert value == datetime.now().year
        return value

    @field_validator("status_code", mode="before")
    @classmethod
    def format_str(cls, value: str) -> str:
        return value.lower().replace(".", " ").replace(" (плюсодин)", "").strip()

    @field_validator("role_code", mode="before")
    @classmethod
    def role_code_prepare(cls, value: str) -> str:
        if value == "Зам.руководителя":
            return "Зам. руководителя"
        elif value == "Свои (плюсодин)":
            return "Свои (плюсодины)"
        return value

    @field_serializer("role_code", "status_code")
    @classmethod
    def serialize_enum(self, strenum: StrEnum, _info) -> str:
        return strenum.name
