from uuid import UUID

from pydantic import BaseModel, Field, computed_field

from app.schemas.notion.primitives.base import BaseNotionModel


class RelationBody(BaseModel):
    id: str | UUID | None
    title: str | None = None
    properties: dict = Field(default_factory=dict)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class Relation(BaseNotionModel):
    relation: list[RelationBody]
    has_more: bool

    @classmethod
    def create_model(cls, values: list[str | UUID | dict], has_more: bool = False):
        result = []
        for value in values:
            if isinstance(value, UUID):
                result.append({"id": value.hex})
            elif isinstance(value, str) or value is None:
                result.append({"id": value})
            elif isinstance(value, dict):
                if isinstance(value.get('id'), UUID):
                    value['id'] = value['id'].hex
                result.append(value)
            else:
                raise ValueError(f"{type(value)=}, {value=} is a wrong type")
        return cls.model_validate(
            dict(
                has_more=has_more,
                relation=[RelationBody.model_validate(x) for x in result],
            )
        )
