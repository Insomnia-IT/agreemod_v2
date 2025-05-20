from enum import StrEnum
from uuid import UUID

from dictionaries.dictionaries import ParticipationRole, ParticipationStatus
from pydantic import BaseModel, Field, field_serializer


class EngagementResponse(BaseModel):
    id: UUID
    deleted: bool = False
    year: int
    person: int | UUID
    role: ParticipationRole
    position: str | None = Field(..., validation_alias="role")
    status: ParticipationStatus | None
    direction: int | UUID

    @field_serializer("role", "status")
    def serialize_enums(self, strenum: StrEnum, _info):
        if not strenum:
            return None
        return strenum.name
