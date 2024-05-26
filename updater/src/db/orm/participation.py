from database.orm.participation import ParticipationORM
from updater.src.notion.models.participation import Participation
from updater.src.notion.models.primitives.base import Text
from updater.src.notion.models.primitives.relation import Relation, RelationBody
from updater.src.notion.models.primitives.rich_text import RichText, RichTextBody
from updater.src.notion.models.primitives.select import Select


class ParticipationUpdORM(ParticipationORM):
    def to_model(self) -> Participation:
        Participation.create_model({
            x: y for x, y in dict(self).items()
        })