from uuid import UUID

from pydantic import BaseModel, Field, computed_field

from updater.src.notion.models.primitives.base import BaseNotionModel


class RelationBody(BaseModel):
    id: UUID
    title: str | None = None
    properties: dict = Field(default_factory=dict)

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
    
    @classmethod
    def create_model(
        cls,
        values: list[str | UUID | dict],
        has_more: bool = False
    ):
        result = []
        for value in values:
            if isinstance(value, UUID):
                result.append({'id': value})
            elif isinstance(value, str):
                print(value)
                result.append({'id': UUID(value)})
            elif isinstance(value, dict):
                result.append(value)
            else:
                raise ValueError(f'{type(value)=}, {value=} is a wrong type')
        return cls.model_validate(
            dict(has_more=has_more,
            relation=[
                RelationBody.model_validate(x) for x in result
            ])
        )