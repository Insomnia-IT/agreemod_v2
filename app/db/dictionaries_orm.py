from database.orm.dictionaries.badge_color import BadgeColorORM
from database.orm.dictionaries.direction_type import DirectionTypeORM
from database.orm.dictionaries.participation_role import ParticipationRoleORM
from database.orm.dictionaries.participation_status import ParticipationStatusORM
from database.orm.dictionaries.participation_type import ParticipationTypeORM
from database.orm.dictionaries.transport_type import TransportTypeORM
from dictionaries.badge_color import BadgeColor
from dictionaries.direction_type import DirectionType
from dictionaries.participation_role import ParticipationRole
from dictionaries.participation_status import ParticipationStatus
from dictionaries.participation_type import ParticipationType
from dictionaries.transport_type import TransportType


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


class ParticipationRoleAppORM(ParticipationRoleORM):
    @classmethod
    def fill_table(cls):
        return [
            cls(
                code=x.name,
                name=x.value,
                is_lead=x.is_lead,
                is_team=x.is_team,
                is_free_feed=x.free_feed,
            )
            for x in ParticipationRole
        ]


class ParticipationTypeAppORM(ParticipationTypeORM):
    @classmethod
    def fill_table(cls):
        return [
            cls(
                code=x.name,
                name=x.value,
                badge_color=x.badge_color.name,
            )
            for x in ParticipationType
        ]


class ParticipationStatusAppORM(ParticipationStatusORM):
    @classmethod
    def fill_table(cls):
        return [
            cls(
                code=x.name,
                name=x.value,
                to_list=x.to_list,
            )
            for x in ParticipationStatus
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
