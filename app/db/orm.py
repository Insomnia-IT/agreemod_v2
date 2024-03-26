from typing import Self

from dictionaries.badge_color import BadgeColor
from dictionaries.direction_type import DirectionType
from dictionaries.participation_role import ParticipationRole
from dictionaries.participation_status import ParticipationStatus
from dictionaries.participation_type import ParticipationType
from dictionaries.transport_type import TransportType
from sqlalchemy.orm import Mapped, relationship

from app.models.arrival import Arrival
from app.models.badge import Badge
from app.models.direction import Direction
from app.models.participation import Participation
from app.models.person import Person
from db.orm.arrival import ArrivalORM
from db.orm.badge import BadgeORM
from db.orm.dictionaries.badge_color import BadgeColorORM
from db.orm.dictionaries.direction_type import DirectionTypeORM
from db.orm.dictionaries.participation_role import ParticipationRoleORM
from db.orm.dictionaries.participation_status import ParticipationStatusORM
from db.orm.dictionaries.participation_type import ParticipationTypeORM
from db.orm.dictionaries.transport_type import TransportTypeORM
from db.orm.direction import DirectionORM
from db.orm.participation import ParticipationORM
from db.orm.person import PersonORM


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
                badge_color=x.badge_color.name,
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


class PersonAppORM(PersonORM):
    @classmethod
    def to_orm(cls, person: Person) -> Self:
        return cls(
            name=person.name,
            last_name=person.last_name,
            first_name=person.first_name,
            nickname=person.nickname,
            other_names=person.other_names,
            gender=person.gender,
            birth_date=person.birth_date,
            city=person.city,
            telegram=person.telegram,
            phone=person.phone,
            email=person.email,
            diet=person.diet,
            comment=person.comment,
            notion_id=person.notion_id.hex,
        )

    def to_model(self) -> Person:
        person = Person(
            name=self.name,
            last_name=self.last_name,
            first_name=self.first_name,
            nickname=self.nickname,
            other_names=self.other_names,
            gender=self.gender,
            birth_date=self.birth_date,
            city=self.city,
            telegram=self.telegram,
            phone=self.phone,
            email=self.email,
            diet=self.diet,
            comment=self.comment,
            notion_id=self.notion_id,
        )
        return person


class DirectionAppORM(DirectionORM):
    direction_type: Mapped[DirectionTypeAppORM] = relationship("DirectionTypeORM")

    @classmethod
    def to_orm(cls, model: Direction):
        return cls(
            name=model.name,
            type=model.type.name,
            first_year=model.first_year,
            last_year=model.last_year,
            notion_id=model.notion_id.hex,
        )

    def to_model(self) -> Direction:
        return Direction(
            name=self.name,
            type=self.direction_type.name,
            first_year=self.first_year,
            last_year=self.last_year,
            notion_id=self.notion_id,
        )


class BadgeAppORM(BadgeORM):
    participation: Mapped[ParticipationTypeAppORM] = relationship(
        "ParticipationTypeORM"
    )
    role: Mapped[ParticipationRoleAppORM] = relationship("ParticipationRoleORM")
    person: Mapped[PersonAppORM] = relationship("PersonORM")
    direction: Mapped[DirectionAppORM] = relationship("DirectionORM")

    @classmethod
    def to_orm(cls, model: Badge) -> Self:
        return cls(
            name=model.name,
            last_name=model.last_name,
            first_name=model.first_name,
            nickname=model.nickname,
            gender=model.gender,
            phone=model.phone,
            infant=model.infant,
            diet=model.diet,
            feed=model.feed,
            number=model.number,
            batch=model.batch,
            participation=model.participation.name,
            role=model.role.name if model.role else None,
            photo=model.photo,
            person_id=model.person.notion_id.hex if model.person else None,
            direction_id=model.direction.notion_id.hex if model.direction else None,
            comment=model.comment,
            notion_id=model.notion_id.hex,
        )

    def to_model(self) -> Badge:
        return Badge(
            name=self.name,
            last_name=self.last_name,
            first_name=self.first_name,
            nickname=self.nickname,
            gender=self.gender,
            phone=self.phone,
            infant=self.infant,
            diet=self.diet,
            feed=self.feed,
            number=self.number,
            batch=self.batch,
            participation=self.participation.name,
            role=self.role.name,
            photo=self.photo,
            person=self.person.to_model(),
            direction=self.direction.to_model(),
            comment=self.comment,
            notion_id=self.notion_id,
        )


class ArrivalAppORM(ArrivalORM):
    badge: Mapped[BadgeAppORM] = relationship("BadgeORM")

    @classmethod
    def to_orm(cls, model: Arrival) -> Self:
        return cls(
            badge_id=model.badge.notion_id,
            arrival_date=model.arrival_date,
            arrival_transport=model.arrival_transport,
            arrival_registered=model.arrival_registered,
            departure_date=model.departure_date,
            departure_transport=model.departure_transport,
            departure_registered=model.departure_registered,
            extra_data=model.extra_data,
            comment=model.comment,
        )

    def to_model(self) -> Arrival:
        return Arrival(
            badge=self.badge.to_model(),
            arrival_date=self.arrival_date,
            arrival_transport=self.arrival_transport,
            arrival_registered=self.arrival_registered,
            departure_date=self.departure_date,
            departure_transport=self.departure_transport,
            departure_registered=self.departure_registered,
            extra_data=self.extra_data,
            comment=self.comment,
        )


class ParticipationAppORM(ParticipationORM):
    person: Mapped[PersonAppORM] = relationship("PersonORM")
    direction: Mapped[DirectionAppORM] = relationship("DirectionORM")
    role: Mapped[ParticipationRoleAppORM] = relationship("ParticipationRoleORM")
    status: Mapped[ParticipationStatusAppORM] = relationship("ParticipationStatusORM")
    participation: Mapped[ParticipationTypeAppORM] = relationship(
        "ParticipationTypeORM"
    )

    @classmethod
    def to_orm(cls, model: Participation):
        return cls(
            year=model.year,
            person_id=model.person.notion_id,
            direction_id=model.direction.notion_id,
            role=model.role_code,
            participation=model.participation.name,
            status=model.status.name,
            notion_id=model.notion_id,
        )

    def to_model(self) -> Participation:
        return Participation(
            year=self.year,
            person=self.person.to_model(),
            direction=self.direction.to_model(),
            role=self.role.code,
            participation=self.participation.code,
            status=self.status.code,
            notion_id=self.notion_id,
        )
