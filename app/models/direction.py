from dictionaries.direction_type import DirectionType

from app.models.base import DomainModel


class Direction(DomainModel):
    name: str | None = None
    type: DirectionType | None = None
    first_year: int | None = None
    last_year: int | None = None

    class Config:
        from_attributes = True

    @classmethod
    def from_notion_data(cls, data_raw, notion_id):
        name = (
            data_raw.get("Name", {})
            .get("title", [{}])[0]
            .get("text", {})
            .get("content")
        )
        type_ = data_raw.get("Тип", {}).get("select", {}).get("name")
        first_year = data_raw.get("Год появления", {}).get("number")
        last_year = data_raw.get("Последний год", {}).get("number")

        return cls(
            name=name,
            type=type_,
            first_year=first_year,
            last_year=last_year,
            notion_id=notion_id,
        )
