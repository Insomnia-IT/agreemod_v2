from datetime import datetime
from uuid import UUID

from dictionaries.participation_role import ParticipationRole
from dictionaries.participation_status import ParticipationStatus
from dictionaries.participation_type import ParticipationType
from pydantic import BaseModel, Field, field_validator


class CodaParticipation(BaseModel):
    coda_index: int = Field(..., alias="id")
    year: int = Field(..., alias="Год")
    person_id: UUID = Field(..., alias="person_id")
    direction_id: UUID = Field(..., alias="direction_id")
    role_code: ParticipationRole = Field(..., alias="Роль")
    participation_code: ParticipationType = Field(..., alias="Роль")
    status_code: ParticipationStatus = Field(..., alias="Статус")
    notion_id: UUID | None = None
    last_updated: datetime = Field(default_factory=datetime.now)

    @field_validator("year")
    @classmethod
    def filter_year(cls, value: int) -> int:
        assert value == datetime.now().year
        return value

    @field_validator("role_code", "participation_code", "status_code", mode="before")
    @classmethod
    def format_str(cls, value: str) -> str:
        return value.lower().replace(".", " ").replace(" (плюсодин)", "").strip()

    @field_validator("role_code", mode="after")
    @classmethod
    def format_role(cls, value: str) -> str:
        return ParticipationRole(value).name

    @field_validator("participation_code", mode="after")
    @classmethod
    def format_type(cls, value: str) -> str:
        return ParticipationType(value).name

    @field_validator("status_code", mode="after")
    @classmethod
    def format_status(cls, value: str) -> str:
        return ParticipationStatus(value).name
