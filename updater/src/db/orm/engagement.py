from database.orm.engagement import EngagementORM
from updater.src.notion.models.engagement import Engagement


class EngagementUpdORM(EngagementORM):
    def to_model(self) -> Engagement:
        Engagement.create_model({x: y for x, y in dict(self).items()})

