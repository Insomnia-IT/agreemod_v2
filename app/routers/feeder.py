import logging

from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.feeder.faker import generate_random_response_model_get
from app.models.feeder.response import RequestModelPOST, ResponseModelGET


logger = logging.getLogger(__name__)
router_feeder = APIRouter(tags=["feeder"])


@router_feeder.get(
    "/feeder/sync",
    summary="API для синхронизации с кормителем. Пока возвращает MOCK данные",
    response_model=ResponseModelGET,
)
async def sync(from_date: datetime):
    """
    API находится в разработке и пока возвращает mock данные.
    """
    logger.info(from_date)
    logger.info(f"from date: {from_date}")
    data = generate_random_response_model_get()
    return data


@router_feeder.post("/feeder/back-sync", summary="API для синхронизации с кормителем")
async def back_sync(arrival: RequestModelPOST):
    logger.debug(arrival)
    msg = "Данные прошли валидацию. Запись в бд находится в процессе разработки."
    return JSONResponse(status_code=200, content={"message": f"OK. {msg}"})
