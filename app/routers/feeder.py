import logging

from datetime import datetime
from typing import Any, Union

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db.repos.arrival import ArrivalRepo
from app.db.repos.badge import BadgeRepo
from app.db.repos.direction import DirectionRepo
from app.db.repos.participation import ParticipationRepo
from app.db.repos.person import PersonRepo
from app.models.arrival import Arrival
from app.models.badge import Badge
from app.models.feeder.faker import generate_random_response_model_get
from app.models.feeder.response import RequestModelPOST, ResponseModelGET
from database.meta import async_session

from app.models.feeder.arrival import Arrival as ArrivalFeeder
from app.models.feeder.badge import Badge as BadgeFeeder
from app.models.feeder.engagement import Engagement as EngagementFeeder
from app.models.feeder.person import Person as PersonFeeder
from app.models.feeder.directions import Direction as DirectionFeeder

logger = logging.getLogger(__name__)
router_feeder = APIRouter()


@router_feeder.get(
    "/feeder/sync",
    summary="API для синхронизации с кормителем.",
    response_model=ResponseModelGET,
)
async def sync(from_date: datetime):
    async with async_session() as session:
        repo_arrival = ArrivalRepo(session)
        arrivals = await repo_arrival.retrieve_all(1, 10)

        repo_badges = BadgeRepo(session)
        badges = await repo_badges.retrieve_all_2(1, 10)

        # TODO: add engagements from https://insomnia-it.github.io/feed/#/default/get_sync
        repo_part = ParticipationRepo(session)
        participations = await repo_part.retrieve_all(1, 10)

        repo_persons = PersonRepo(session)
        persons = await repo_persons.retrieve_all(1, 10)

        repo_directions = DirectionRepo(session)
        directions = await repo_directions.retrieve_all_2(1, 10)

    resp = ResponseModelGET(
        badges=convert_objects(badges, BadgeFeeder),
        arrivals=convert_objects(arrivals, ArrivalFeeder),
        engagements=convert_objects(participations, EngagementFeeder),
        persons=convert_objects(persons, PersonFeeder),
        directions=convert_objects(directions, DirectionFeeder),
    )

    return resp


def convert_objects(data: list, dist_model: Union[type(ArrivalFeeder)]) -> list:
    results = []
    for i in data:
        try:
            results.append(dist_model.from_db(i))
        except Exception as e:
            logger.critical(f"Error converting object {i}: {e}")
    return results


@router_feeder.post("/feeder/back-sync", summary="API для синхронизации с кормителем")
async def back_sync(data: RequestModelPOST):
    async with async_session() as session:

        repo_arrival = ArrivalRepo(session)
        for arrival in data.arrivals:
            db_obj = Arrival.from_feeder(actor_badge=arrival.actor_badge, data=arrival.data)
            await repo_arrival.update2(db_obj)

        repo_badge = BadgeRepo(session)
        for badge in data.badges:
            db_obj = Badge.from_feeder(actor_badge=badge.actor_badge, data=badge.data)
            await repo_badge.update_2(db_obj)

    logger.debug(data)
    msg = "Данные прошли валидацию и сохранены в бд."
    return JSONResponse(status_code=200, content={"message": f"OK. {msg}"})
