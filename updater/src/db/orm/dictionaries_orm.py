from database.orm.dictionaries.badge_color import BadgeColorORM
from database.orm.dictionaries.direction_type import DirectionTypeORM
from database.orm.dictionaries.engagement_role import EngagementRoleORM
from database.orm.dictionaries.engagement_status import EngagementStatusORM
from database.orm.dictionaries.transport_type import TransportTypeORM
from dictionaries.badge_color import BadgeColor
from dictionaries.direction_type import DirectionType
from dictionaries.engagement_status import EngagementStatus
from dictionaries.transport_type import TransportType
from updater.src.notion.models.dictionaries.engagement_role import (
    EngagementRoleNotion,
)
from updater.src.utils import convert_model, query_notion_database


class BadgeColorAppORM(BadgeColorORM):
    @classmethod
    def fill_table(cls):
        return [
            cls(
                code=x.name,
                color=x.value,
            )
            for x in BadgeColor
        ]


class DirectionTypeAppORM(DirectionTypeORM):
    @classmethod
    def fill_table(cls):
        return [
            cls(
                code=x.name,
                name=x.value,
                is_federal=x.is_federal,
            )
            for x in DirectionType
        ]


class EngagementRoleAppORM(EngagementRoleORM):
    @classmethod
    def fill_table(cls):
        roles_raw = query_notion_database("bae439d794944ccfb361774f57d6b43d")
        roles = [EngagementRoleNotion.model_validate(x) for x in roles_raw]
        return [cls(**convert_model(x)) for x in roles]


class EngagementStatusAppORM(EngagementStatusORM):
    @classmethod
    def fill_table(cls):
        return [
            cls(
                code=x.name,
                name=x.value,
                to_list=x.to_list,
            )
            for x in EngagementStatus
        ]


class TransportTypeAppORM(TransportTypeORM):
    @classmethod
    def fill_table(cls):
        return [
            cls(
                code=x.name,
                name=x.value,
            )
            for x in TransportType
        ]
