import logging

from fastapi import APIRouter

from app.services.photo_sync import PhotoSyncService


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/{record_id}",
    summary="Синхронизация фотографий из Google Drive",
    description="Синхронизация фотографий из Google Drive по record_id из Import_series"
)
async def sync_folder(record_id: int):
    service = PhotoSyncService()
    return await service.sync_folder(record_id)
