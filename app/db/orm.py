from typing import List, Self

from database.orm.arrival import ArrivalORM
from database.orm.badge import AnonsORM, BadgeORM
from database.orm.badge_directions import BadgeDirectionsORM
from database.orm.direction import DirectionORM
from database.orm.logging import LogsORM
from database.orm.participation import ParticipationORM
from database.orm.person import PersonORM
from dictionaries.dictionaries import DirectionType, ParticipationRole, ParticipationStatus
from dictionaries.diet_type import DietType
from dictionaries.feed_type import FeedType
from dictionaries.gender import Gender
from dictionaries.transport_type import TransportType
from sqlalchemy.orm import Mapped, relationship

from app.dto.badge import BadgeDTO, Parent
from app.models.arrival import Arrival
from app.models.badge import Anons, Badge, DirectionDTO
from app.models.direction import Direction
from app.models.logging import Logs
from app.models.participation import Participation
from app.models.person import Person


class PersonAppORM(PersonORM):
    @classmethod
    def to_orm(cls, person: Person) -> Self:
        return cls(
            id=person.id,
            name=person.name,
            last_name=person.last_name,
            first_name=person.first_name,
            nickname=person.nickname,
            other_names=person.other_names,
            gender=person.gender.value if person.gender else Gender.OTHER.value,
            birth_date=person.birth_date,
            city=person.city,
            telegram=person.telegram,
            phone=person.phone,
            email=person.email,
            diet=person.diet.value if person.diet else DietType.STANDARD.value,
            comment=person.comment,
            notion_id=person.notion_id.hex,
            last_updated=person.last_updated,
        )

    def to_model(self) -> Person:
        person = Person(
            id=self.id,
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
            last_updated=self.last_updated,
        )
        return person


class DirectionAppORM(DirectionORM):
    badges: Mapped[List["BadgeDirectionsAppORM"]] = relationship(back_populates="direction", lazy="selectin")

    @classmethod
    def to_orm(cls, model: Direction):
        return cls(
            id=model.id,
            name=model.name,
            type=model.type.name,
            first_year=model.first_year,
            last_year=model.last_year,
            notion_id=model.notion_id.hex,
            last_updated=model.last_updated,
        )

    def to_model(self, include_badges: bool = False) -> Direction:
        return Direction(
            id=self.id,
            name=self.name,
            type=DirectionType[self.type].value,
            first_year=self.first_year,
            last_year=self.last_year,
            notion_id=self.notion_id,
            last_updated=self.last_updated,
            badges=(
                [BadgeDTO.model_validate(x.badge, from_attributes=True) for x in self.badges] if include_badges else []
            ),
        )


class BadgeAppORM(BadgeORM):
    parent: Mapped["BadgeAppORM"] = relationship("BadgeAppORM", lazy="selectin")
    person: Mapped[PersonAppORM] = relationship("PersonAppORM", lazy="selectin")
    directions: Mapped[List["BadgeDirectionsAppORM"]] = relationship(back_populates="badge", lazy="selectin")

    @classmethod
    def to_orm(cls, model: Badge) -> Self:
        return cls(
            id=model.id,
            name=model.name,
            last_name=model.last_name,
            first_name=model.first_name,
            nickname=model.nickname,
            gender=model.gender,
            phone=model.phone,
            parent_id=model.parent.id if model.parent else None,
            child=model.child,
            diet=(
                model.diet.name if model.diet else DietType.STANDARD.name
            ),  # if isinstance(model.diet, DietType) else DietType.default(),
            feed=model.feed if model.feed else FeedType.NO.name,
            number=model.number,
            batch=model.batch,
            role_code=model.role.name,  # if isinstance(model.role, ParticipationRole) else ParticipationRole(model.role).name if model.role else None,
            photo=model.photo,
            occupation=model.occupation,
            person_id=model.person.id if model.person else None,
            comment=model.comment,
            notion_id=model.notion_id.hex if model.notion_id else None,
        )

    def to_model(
        self,
        include_person: bool = False,
        include_directions: bool = False,
        include_parent: bool = False,
    ) -> Badge:
        return Badge(
            id=self.id,
            name=self.name,
            last_name=self.last_name,
            first_name=self.first_name,
            nickname=self.nickname,
            gender=self.gender,
            phone=self.phone,
            parent=(
                Parent.model_validate(self.parent, from_attributes=True)
                if self.parent and include_parent
                else self.parent_id
            ),
            child=self.child,
            diet=DietType[self.diet].value if self.diet else None,
            feed=FeedType[self.feed].value if self.feed else None,
            number=self.number,
            batch=self.batch,
            role=ParticipationRole[self.role_code].value,
            photo=self.photo,
            person=self.person.to_model() if self.person and include_person else self.person_id,
            directions=(
                [DirectionDTO.model_validate(x.direction, from_attributes=True) for x in self.directions]
                if include_directions
                else None
            ),
            occupation=self.occupation,
            comment=self.comment,
            notion_id=self.notion_id,
            last_updated=self.last_updated,
        )


class ArrivalAppORM(ArrivalORM):
    badge: Mapped[BadgeAppORM] = relationship("BadgeAppORM", lazy="selectin")

    @classmethod
    def to_orm(cls, model: Arrival) -> Self:
        return cls(
            id=model.id,
            badge_id=model.badge.id if isinstance(model.badge, Badge) else model.badge,
            arrival_date=model.arrival_date,
            arrival_transport=model.arrival_transport.name,  # if isinstance(model.arrival_transport, TransportType) else model.arrival_transport,
            arrival_registered=model.arrival_registered.isoformat() if model.arrival_registered else None,
            departure_date=model.departure_date,
            departure_transport=model.departure_transport.name,  # if isinstance(model.departure_transport, TransportType) else model.departure_transport,
            departure_registered=model.departure_registered.isoformat() if model.departure_registered else None,
            status=model.status.name,  # if isinstance(model.status, ParticipationStatus) else model.status,
            extra_data=model.extra_data,
            comment=model.comment,
            last_updated=model.last_updated,
            coda_index=model.coda_index,
        )

    def to_model(self, include_badge: bool = False) -> Arrival:
        return Arrival(
            id=self.id,
            badge=(BadgeDTO.model_validate(self.badge, from_attributes=True) if include_badge else self.badge_id),
            arrival_date=self.arrival_date,
            arrival_transport=TransportType[self.arrival_transport].value if self.arrival_transport else None,
            arrival_registered=self.arrival_registered,
            departure_date=self.departure_date,
            departure_transport=TransportType[self.departure_transport].value if self.departure_transport else None,
            departure_registered=self.departure_registered,
            status=ParticipationStatus[self.status].value if self.status else None,
            extra_data=self.extra_data,
            comment=self.comment,
            last_updated=self.last_updated,
            coda_index=self.coda_index,
        )


class ParticipationAppORM(ParticipationORM):
    person: Mapped[PersonAppORM] = relationship("PersonAppORM", lazy="selectin")
    direction: Mapped[DirectionAppORM] = relationship("DirectionAppORM", lazy="selectin")

    @classmethod
    def to_orm(cls, model: Participation):
        return cls(
            id=model.id,
            year=model.year,
            person_id=model.person.id,
            direction_id=model.direction.id,
            role_code=model.role.name,
            status_code=model.status.name,
            notion_id=model.notion_id,
            last_updated=model.last_updated,
        )

    def to_model(self, include_person: bool = False, include_direction: bool = False) -> Participation:
        return Participation(
            year=self.year,
            person=self.person.to_model() if include_person else self.person_id,
            direction=(
                DirectionDTO.model_validate(self.direction, from_attributes=True)
                if include_direction
                else self.direction_id
            ),
            role=ParticipationRole[self.role_code].value.capitalize() if self.role_code else None,
            status=ParticipationStatus[self.status_code].value if self.status_code else None,
            notion_id=self.notion_id,
            last_updated=self.last_updated,
        )


class BadgeDirectionsAppORM(BadgeDirectionsORM):
    badge: Mapped[BadgeAppORM] = relationship(back_populates="directions", lazy="selectin")
    direction: Mapped[DirectionAppORM] = relationship(back_populates="badges", lazy="selectin")


class LogsAppORM(LogsORM):
    @classmethod
    def to_orm(cls, model: Logs):
        return cls(
            author=model.author,
            table_name=model.table_name,
            row_id=model.row_id,
            operation=model.operation,
            timestamp=model.timestamp,
            new_data=model.new_data,
        )

    def to_model(self):
        return Logs(
            author=self.author,
            table_name=self.table_name,
            row_id=self.row_id,
            operation=self.operation,
            timestamp=self.timestamp,
            new_data=self.new_data,
        )


class AnonsAppORM(AnonsORM):
    def to_model(self):
        return Anons(
            title=self.title,
            subtitle=self.subtitle,
            batch=self.batch,
            color=self.color,
            quantity=self.quantity,
            to_print=self.to_print,
        )
