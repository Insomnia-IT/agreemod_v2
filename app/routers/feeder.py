import logging

from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db.repos.arrival import ArrivalRepo
from app.db.repos.badge import BadgeRepo
from app.models.arrival import Arrival
from app.models.badge import Badge
from app.models.feeder.faker import generate_random_response_model_get
from app.models.feeder.response import RequestModelPOST, ResponseModelGET
from database.meta import async_session

logger = logging.getLogger(__name__)
router_feeder = APIRouter()


@router_feeder.get(
    "/feeder/sync",
    summary="API для синхронизации с кормителем. Пока возвращает MOCK данные",
    response_model=ResponseModelGET,
)
async def sync(from_date: datetime):
    logger.info(from_date)
    logger.info(f"from date: {from_date}")
    data = generate_random_response_model_get()
    return data


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
