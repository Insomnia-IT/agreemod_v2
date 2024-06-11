from pydantic import BaseModel


class Direction(BaseModel):
    id: str | None = None
    deleted: bool | None = None
    name: str | None = None
    first_year: int | None = None
    last_year: int | None = None
    type: str | None = None
    notion_id: str | None = None

    @staticmethod
    def from_db(direction: "DirectionDB") -> "Direction":
        return Direction(
            id=str(direction.id) if direction.id else None,
            name=direction.name,
            first_year=direction.first_year,
            last_year=direction.last_year,
            type=direction.type.value if direction.type else None,
            notion_id=str(direction.notion_id) if direction.notion_id else None,
        )
