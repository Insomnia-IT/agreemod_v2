import logging

from fastapi import APIRouter

from app.services.photo.photo_import import PhotoImportService


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/photo-import",
    summary="Импорт фотографий для всех серий",
    description="Импорт фотографий из Google Drive для всех записей Import_series",
)
async def import_all():
    service = PhotoImportService()
    return await service.import_all()


@router.post(
    "/photo-import/{record_id}",
    summary="Импорт фотографий для одной серии",
    description="Импорт фотографий из Google Drive для указанной записи Import_series",
)
async def import_one(record_id: int):
    service = PhotoImportService()
    return await service.import_one(record_id)
