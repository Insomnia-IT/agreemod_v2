import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.feeder.faker import generate_random_response_model_get
from app.models.feeder.response import RequestModelPOST, ResponseModelGET

logger = logging.getLogger(__name__)
router_feeder = APIRouter(tags=["feeder"])


@router_feeder.get(
    "/feeder/sync",
    summary="API для синхронизации с кормителем. Пока возвращает MOCK данные",
    response_model=ResponseModelGET
)
async def create_arrival():
    """
    API находится в разработке и пока возвращает mock данные.
    """
    data = generate_random_response_model_get()
    return data


@router_feeder.post(
    "/feeder/back-sync",
    summary="API для синхронизации с кормителем"
)
async def create_arrival(arrival: RequestModelPOST):
    logger.debug(arrival)
    msg = "Данные прошлы валидацию. Запись в бд находится в процессе разработки."
    return JSONResponse(
        status_code=200,
        content={"message": f"OK. {msg}"})
