import logging

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse

from app.dependencies.service import get_feeder_service
from app.schemas.feeder.requests import BackSyncIntakeSchema, SyncResponseSchema
from app.services.feeder import FeederService
from app.utils.verify_credentials import verify_credentials


logger = logging.getLogger(__name__)
router_feeder = APIRouter()


@router_feeder.get(
    "/feeder/sync",
    summary="API для синхронизации с кормителем. Пока возвращает MOCK данные",
    response_model=SyncResponseSchema,
)
async def sync(
    username: Annotated[str, Depends(verify_credentials)],
    from_date: datetime,
    service: FeederService = Depends(get_feeder_service),
):
    return await service.sync(from_date)


@router_feeder.post("/feeder/back-sync", summary="API для синхронизации с кормителем")
async def back_sync(
    username: Annotated[str, Depends(verify_credentials)],
    intake: BackSyncIntakeSchema,
    background_tasks: BackgroundTasks,
    badges_service: FeederService = Depends(get_feeder_service),
    arrivals_service: FeederService = Depends(get_feeder_service),
    badges_bg_service: FeederService = Depends(get_feeder_service),
    arrivals_bg_service: FeederService = Depends(get_feeder_service),

):
    badges = await badges_service.back_sync_badges(intake)
    to_update, to_delete = await arrivals_service.back_sync_arrivals(intake)
    background_tasks.add_task(badges_bg_service.update_notion_badges, badges)
    background_tasks.add_task(arrivals_bg_service.update_coda_arrivals, to_update, to_delete)
    return JSONResponse(status_code=200, content={"message": "синхронизация базы завершена, запущена синхронизация ноушена и коды"})

    # await badges_service.back_sync_badges(intake)
    # await arrivals_service.back_sync_arrivals(intake)
    # return JSONResponse(status_code=200, content={"message": "OK"})
