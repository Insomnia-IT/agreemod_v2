from pydantic import BaseModel


class Engagement(BaseModel):
    id: str | None = None
    deleted: bool | None = None
    year: int | None = None
    person: str | None = None
    role: str | None = None
    position: str | None = None
    status: str | None = None
    direction: str | None = None
    notion_id: str | None = None

    @staticmethod
    def from_db(participation: "Participation") -> "Engagement":
        return Engagement(
            id=str(participation.id) if participation.id else None,
            year=participation.year,
            person=str(participation.person) if participation.person else None,
            role=participation.role.value if participation.role else None,
            position=None,  # Нет информации о position в объекте Participation
            status=participation.status.value if participation.status else None,
            direction=str(participation.direction) if participation.direction else None,
            notion_id=str(participation.notion_id) if participation.notion_id else None,
        )
