from uuid import UUID

from pydantic import BaseModel


class DomainModel(BaseModel):
    notion_id: UUID
