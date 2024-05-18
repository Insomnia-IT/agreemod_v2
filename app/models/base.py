import uuid
from uuid import UUID

from pydantic import BaseModel, Field


class DomainModel(BaseModel):
    id: UUID = Field(default_factory=uuid.uuid4)
