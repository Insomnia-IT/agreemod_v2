from uuid import UUID

from dictionaries.direction_type import DirectionType
from pydantic import BaseModel


class DirectionDTO(BaseModel):
    id: UUID
    name: str | None = None
    type: DirectionType | None = None
    notion_id: UUID
