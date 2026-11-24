from database.orm.participation import ParticipationORM
from updater.src.notion.models.participation import Participation


class ParticipationUpdORM(ParticipationORM):
    def to_model(self) -> Participation:
        Participation.create_model({x: y for x, y in dict(self).items()})
