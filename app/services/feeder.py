import logging

from datetime import datetime

from dictionaries.diet_type import DietType
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repos.arrival import ArrivalRepo
from app.db.repos.badge import BadgeRepo
from app.db.repos.direction import DirectionRepo
from app.db.repos.logging import LogsRepo
from app.db.repos.participation import ParticipationRepo
from app.db.repos.person import PersonRepo
from app.models.arrival import Arrival
from app.models.badge import Badge
from app.models.logging import Logs
from app.schemas.feeder.arrival import ArrivalResponse, ArrivalWithMetadata
from app.schemas.feeder.badge import BadgeResponse, BadgeWithMetadata
from app.schemas.feeder.directions import DirectionResponse
from app.schemas.feeder.engagement import EngagementResponse
from app.schemas.feeder.person import PersonResponse
from app.schemas.feeder.requests import BackSyncIntakeSchema, SyncResponseSchema


logger = logging.getLogger(__name__)


class FeederService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.badges = BadgeRepo(session)
        self.directions = DirectionRepo(session)
        self.arrivals = ArrivalRepo(session)
        self.participations = ParticipationRepo(session)
        self.persons = PersonRepo(session)
        self.logs = LogsRepo(session)

    async def process_badge(self, b: BadgeWithMetadata):
        actor = await self.badges.retrieve(b.actor_badge)
        dt = b.date
        exist = await self.badges.retrieve(b.data.notion_id)
        badge = b.data
        if exist and exist.last_updated < dt:
            if not badge.deleted:
                model = Badge(
                    id=exist.id,
                    name=badge.name,
                    last_name=badge.last_name,
                    first_name=badge.first_name,
                    nickname=exist.nickname,
                    gender=badge.gender,
                    phone=badge.phone,
                    infant=(
                        exist.infant if badge.infant else None
                    ),  # TODO: уточнить что делать с этим полем, feeder присылает bool (is_infant)
                    diet=DietType.VEGAN if badge.vegan else DietType.default(),
                    feed=badge.feed,
                    number=badge.number,
                    batch=badge.batch,
                    role=badge.role,
                    photo=badge.photo,
                    person=badge.person,
                    comment=badge.comment,
                    notion_id=badge.notion_id,
                    last_updated=dt,
                    directions=badge.directions,
                )
                await self.badges.update(model)
        elif not exist:
            model = Badge(
                name=badge.name,
                last_name=badge.last_name,
                first_name=badge.first_name,
                nickname=None,
                gender=badge.gender,
                phone=badge.phone,
                infant=None,  # TODO: уточнить что делать с этим полем, feeder присылает bool (is_infant)
                diet=DietType.VEGAN if badge.vegan else DietType.default(),
                feed=badge.feed,
                number=badge.number,
                batch=badge.batch,
                role=badge.role,
                photo=badge.photo,
                person=badge.person,
                comment=badge.comment,
                notion_id=badge.notion_id,
                last_updated=datetime.now(),
                directions=badge.directions,
            )
            await self.badges.create(model)
        if not badge.deleted:
            await self.logs.add_log(
                Logs(
                    author=actor.name,
                    table_name="badges",
                    row_id=exist.id if exist else None,
                    operation="MERGE" if exist else "INSERT",
                    timestamp=datetime.now(),
                    new_data=model.model_dump(),
                )
            )

    async def process_arrival(self, a: ArrivalWithMetadata):
        actor = await self.badges.retrieve(a.actor_badge)
        dt = a.date
        exist: Arrival = await self.arrivals.retrieve(a.data.id)
        arrival = a.data
        if exist and exist.last_updated < dt:
            if not arrival.deleted:
                model = Arrival(
                    id=exist.id,
                    badge=arrival.badge,
                    arrival_date=arrival.arrival_date.date(),
                    arrival_registered=arrival.arrival_date.time(),
                    departure_date=arrival.departure_date.date(),
                    departure_registered=arrival.departure_date.time(),
                    arrival_transport=arrival.arrival_transport,
                    departure_transport=arrival.departure_transport,
                    extra_data={},
                    comment="",
                    last_updated=a.data,
                )
                await self.arrivals.update(model)
        elif not exist:
            model = Arrival(
                badge=arrival.badge,
                arrival_date=arrival.arrival_date.date(),
                arrival_registered=arrival.arrival_date.time(),
                departure_date=arrival.departure_date.date(),
                departure_registered=arrival.departure_date.time(),
                arrival_transport=arrival.arrival_transport,
                departure_transport=arrival.departure_transport,
                extra_data={},
                comment="",
                last_updated=a.data,
            )
            await self.arrivals.create(model)
        if not arrival.deleted:
            await self.logs.add_log(
                Logs(
                    author=actor.name,
                    table_name="arrivals",
                    row_id=exist.id if exist else None,
                    operation="MERGE" if exist else "INSERT",
                    timestamp=datetime.now(),
                    new_data=model.model_dump(),
                )
            )

    async def back_sync(self, intake: BackSyncIntakeSchema):
        arrivals = intake.arrivals
        badges = intake.badges

        for b in badges:
            await self.process_badge(b)
        for a in arrivals:
            await self.process_arrival(a)

        await self.session.commit()

    async def sync(self, from_date: datetime):
        get_badges = await self.badges.retrieve_many(include_infant=True, include_directions=True, from_date=from_date)
        badges = [BadgeResponse.model_validate(x.model_dump()) for x in get_badges]
        get_arrivals = await self.arrivals.retrieve_all(from_date=from_date)
        arrivals = [ArrivalResponse.model_validate(x.model_dump()) for x in get_arrivals]
        get_engagements = await self.participations.retrieve_all(from_date=from_date)
        engagements = [EngagementResponse.model_validate(x.model_dump()) for x in get_engagements]
        get_persons = await self.persons.retrieve_all(from_date=from_date)
        persons = [PersonResponse.model_validate(x.model_dump()) for x in get_persons]
        get_directions = await self.directions.retrieve_all(from_date=from_date)
        directions = [DirectionResponse.model_validate(x.model_dump()) for x in get_directions]

        response = {
            "badges": badges,
            "arrivals": arrivals,
            "engagements": engagements,
            "persons": persons,
            "directions": directions,
        }
        return SyncResponseSchema.model_validate(response)
