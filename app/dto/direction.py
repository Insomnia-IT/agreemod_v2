from uuid import UUID

from pydantic import BaseModel

from dictionaries.direction_type import DirectionType


class DirectionDTO(BaseModel):
    id: UUID
    name: str | None = None
    type: DirectionType | None = None
    notion_id: UUID
