from enum import StrEnum
from uuid import UUID

from dictionaries.dictionaries import ParticipationRole, ParticipationStatus
from pydantic import BaseModel, Field, field_serializer


class EngagementResponse(BaseModel):
    id: UUID = Field(..., validation_alias='notion_id')
    deleted: bool = False
    year: int
    person: UUID
    role: ParticipationRole
    position: str | None = Field(..., validation_alias="role")
    status: ParticipationStatus
    direction: UUID
    notion_id: UUID | None

    @field_serializer("role", "status")
    def serialize_enums(self, strenum: StrEnum, _info):
        if not strenum:
            return None
        return strenum.name
