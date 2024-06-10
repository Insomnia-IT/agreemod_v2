import logging

from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.dependencies.service import get_feeder_service
from app.schemas.feeder.requests import SyncResponseSchema, BackSyncIntakeSchema
from app.services.feeder import FeederService

logger = logging.getLogger(__name__)
router_feeder = APIRouter(tags=["feeder"])


@router_feeder.get(
    "/feeder/sync",
    summary="API для синхронизации с кормителем. Пока возвращает MOCK данные",
    response_model=SyncResponseSchema,
)
async def sync(
    from_date: datetime,
    service: FeederService = Depends(get_feeder_service)
):
    return await service.sync(from_date)


@router_feeder.post("/feeder/back-sync", summary="API для синхронизации с кормителем")
async def back_sync(
    intake: BackSyncIntakeSchema,
    service: FeederService = Depends(get_feeder_service)   
):
    await service.back_sync(intake)
    return JSONResponse(status_code=200, content={"message": "OK"})
