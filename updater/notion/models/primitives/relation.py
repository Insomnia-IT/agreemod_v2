from uuid import UUID

from pydantic import BaseModel, computed_field
from updater.notion.models.primitives.base import BaseNotionModel


class RelationBody(BaseModel):
    id: UUID
    title: str | None = None
    properties: dict = {}

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class Relation(BaseNotionModel):
    relation: list[RelationBody]
    has_more: bool

    @computed_field
    @property
    def value(self) -> list[UUID]:
        return [r.id for r in self.relation]

    @computed_field
    @property
    def title(self) -> list[str]:
        return [r.title for r in self.relation if r]
