import logging

from fastapi import APIRouter

from app.services.photo_sync import PhotoSyncService


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/photo-sync",
    summary="Синхронизация фотографий для всех серий",
    description="Синхронизация фотографий из Google Drive для всех записей Import_series",
)
async def sync_all():
    service = PhotoSyncService()
    return await service.sync_all()

@router.post(
    "/photo-sync/{record_id}",
    summary="Синхронизация фотографий для одной серии",
    description="Синхронизация фотографий из Google Drive по record_id из Import_series",
)
async def sync(record_id: int):
    service = PhotoSyncService()
    return await service.sync(record_id)
