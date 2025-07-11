import logging

from datetime import date, datetime, time
from enum import Enum
from typing import Any
from uuid import UUID

import asyncpg

from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential

from app.coda.writer import CodaWriter
from app.config import config
from app.db.repos.arrival import ArrivalRepo
from app.db.repos.badge import BadgeRepo
from app.db.repos.direction import DirectionRepo
from app.db.repos.logging import LogsRepo
from app.db.repos.participation import ParticipationRepo
from app.db.repos.person import PersonRepo
from app.models.logging import Logs
from app.models.badge import Badge
from app.schemas.feeder.arrival import ArrivalResponse
from app.schemas.feeder.badge import BadgeResponse
from app.schemas.feeder.directions import DirectionResponse
from app.schemas.feeder.engagement import EngagementResponse
from app.schemas.feeder.person import PersonResponse
from app.schemas.feeder.requests import BackSyncIntakeSchema, SyncResponseSchema
from app.services.badge_to_grist import grist_badges_writer
from app.services.arrivals_to_grist import grist_arrivals_writer
from app.dto.direction import DirectionDTO
from app.services.badge_to_grist import grist_badges_writer
from app.services.arrivals_to_grist import grist_arrivals_writer
from app.dto.direction import DirectionDTO
from dictionaries import FeedType, DietType

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


class WaitForItError(Exception):
    pass


class FeederService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.badges = BadgeRepo(session)
        self.directions = DirectionRepo(session)
        self.arrivals = ArrivalRepo(session)
        self.participations = ParticipationRepo(session)
        self.persons = PersonRepo(session)
        self.logs = LogsRepo(session)
        #self.coda_writer = CodaWriter(api_key=config.coda.api_key, doc_id=config.coda.doc_id)

    async def back_sync_badges(self, intake: BackSyncIntakeSchema):
        badges = intake.badges
        logger.info(badges)
        #TODO: There is no reason to update badges in database here, we can pass them directly to grist
        # and then just fetch them with grist_updater, it seems more correct
        if badges:
            # Extract all IDs of linked entities from intake badges
            person_ids = []
            #parent_ids = []
            direction_ids = []
            
            for badge in badges:
                if badge.data.person:
                    person_ids.append(badge.data.person)
                #if badge.data.parent:
                #    parent_ids.append(badge.data.parent)
                if badge.data.directions:
                    direction_ids.extend(badge.data.directions)
            
            # Get all linked entities from database
            persons = await self.persons.retrieve_many(idIn=person_ids) if person_ids else []
            #parents = await self.badges.retrieve_many(idIn=parent_ids) if parent_ids else []
            directions = await self.directions.retrieve_many(idIn=direction_ids) if direction_ids else []
            
            # Create a mapping of IDs to entities for quick lookup
            person_map = {str(p.id): p for p in persons}
            #parent_map = {str(p.id): p for p in parents}
            direction_map = {str(d.id): DirectionDTO(
                id=d.id,
                name=d.name,
                type=d.type,
                nocode_int_id=d.nocode_int_id
            ) for d in directions}
            # Enrich badges with their linked entities
            enriched_badges = []
            for badge in badges:
                badge_data = badge.data.model_dump()
                # Track which fields were present in the original data
                present_fields = set(badge.data.model_fields_set)
                if badge_data.get('person'):
                    badge_data['person'] = person_map.get(str(badge_data['person']))
                #if badge_data.get('parent'):
                #    badge_data['parent'] = parent_map.get(str(badge_data['parent']))
                if badge_data.get('directions'):
                    badge_data['directions'] = [direction_map.get(str(d)) for d in badge_data['directions'] if direction_map.get(str(d))]
                if badge_data.get("feed"):
                    badge_data['feed'] = FeedType(badge_data['feed']).value
                if badge_data.get('vegan'):
                    badge_data['diet'] = DietType.STANDARD.value if badge_data.get('vegan') else DietType.VEGAN.value
                badge_obj = Badge.model_construct(**badge_data)
                enriched_badges.append((badge_obj, present_fields))  # Store as a tuple of (badge, present_fields)
            
            # Pass enriched badges to Grist writer
            await grist_badges_writer(enriched_badges)


    async def back_sync_arrivals(self, intake: BackSyncIntakeSchema):
        update_arrivals = []
        delete_arrivals = []
        arrivals = intake.arrivals
        if arrivals:
            # Create list of tuples (arrival, present_fields)
            enriched_arrivals = []
            for arrival in arrivals:
                present_fields = set(arrival.data.model_fields_set)
                enriched_arrivals.append((arrival, present_fields))
            await grist_arrivals_writer(enriched_arrivals)

        #await self.session.commit()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def sync(self, from_date: datetime):
        get_badges = await self.badges.retrieve_many(include_parent=True, from_date=from_date, include_directions=True, person_uuid=True) #include_infant=True
        badges = [BadgeResponse.model_validate(x.model_dump()) for x in get_badges]
        get_arrivals = await self.arrivals.retrieve_all(from_date=from_date, badge_uuid=True)
        arrivals = [ArrivalResponse.model_validate(x.model_dump()) for x in get_arrivals]
        get_engagements = await self.participations.retrieve_all(from_date=from_date, uuid_ids=True)
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
