import logging

from datetime import date, datetime, time
from enum import Enum
from typing import Any
from uuid import UUID

import asyncpg

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.coda.writer import CodaWriter
from app.config import config
from app.db.repos.arrival import ArrivalRepo
from app.db.repos.badge import BadgeRepo
from app.db.repos.direction import DirectionRepo
from app.db.repos.logging import LogsRepo
from app.db.repos.participation import ParticipationRepo
from app.db.repos.person import PersonRepo
from app.models.logging import Logs
from app.schemas.feeder.arrival import ArrivalResponse
from app.schemas.feeder.badge import BadgeResponse
from app.schemas.feeder.directions import DirectionResponse
from app.schemas.feeder.engagement import EngagementResponse
from app.schemas.feeder.person import PersonResponse
from app.schemas.feeder.requests import BackSyncIntakeSchema, SyncResponseSchema


logger = logging.getLogger(__name__)


def serialize(data: dict) -> dict:
    def adapt_to_serialize(value: Any):
        if isinstance(value, (asyncpg.pgproto.pgproto.UUID, UUID)):
            return str(value)
        elif isinstance(value, Enum):
            return value.value
        elif isinstance(value, (datetime, date, time)):
            return value.isoformat()
        elif isinstance(value, dict):
            return serialize(value)
        elif isinstance(value, list):
            serialized = []
            for i in value:
                serialized.append(adapt_to_serialize(i))
            return serialized
        else:
            return value

    return {x: adapt_to_serialize(y) for x, y in data.items()}


class FeederService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.badges = BadgeRepo(session)
        self.directions = DirectionRepo(session)
        self.arrivals = ArrivalRepo(session)
        self.participations = ParticipationRepo(session)
        self.persons = PersonRepo(session)
        self.logs = LogsRepo(session)
        self.coda_writer = CodaWriter(api_key=config.coda.api_key, doc_id=config.coda.doc_id)

    async def back_sync(self, intake: BackSyncIntakeSchema):
        arrivals = intake.arrivals
        badges = intake.badges
        if badges:
            existing = await self.badges.update_feeder([x.data for x in badges])
            for e, b in zip(existing, badges):
                actor = await self.badges.retrieve(b.actor_badge)
                dt = b.date.replace(tzinfo=None)
                await self.logs.add_log(
                    Logs(
                        author=actor.name if actor else "ANON",
                        table_name="badge",
                        row_id=b.data.id if e else None,
                        operation="MERGE" if e else "INSERT" if e is not None else "DELETE",
                        timestamp=dt,
                        new_data=serialize(b.data.model_dump() if e is not None else {}),
                    )
                )
        if arrivals:
            created = await self.arrivals.update_feeder([x.data for x in arrivals])
            for e, a in zip(created, arrivals):
                actor = await self.badges.retrieve(a.actor_badge)
                dt = a.date.replace(tzinfo=None)
                await self.logs.add_log(
                    Logs(
                        author=actor.name if actor else "ANON",
                        table_name="arrival",
                        row_id=a.data.id if e and e.coda_index is not None else None,
                        operation="MERGE" if e and e.coda_index is not None else "INSERT" if e is not None else "DELETE",
                        timestamp=dt,
                        new_data=serialize(a.data.model_dump() if e is not None else {}),
                    )
                )
                if e:
                    coda_index = await self.coda_writer.update_arrival(self.arrivals, a.data)
                    e.coda_index = coda_index
                    await self.session.merge(e)

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
