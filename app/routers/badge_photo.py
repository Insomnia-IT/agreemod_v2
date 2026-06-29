import logging

from fastapi import APIRouter

from app.services.photo.badge_photo import BadgePhotoService


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/badge-photo-import",
    summary="Импорт фотографий для бейджей из Google Drive",
    description="Создание записей Photo с фотографиями из Google Drive и добавление ссылки на созданные записи в поле photo таблицы Badges_2026",
)
async def badge_photo_import():
    service = BadgePhotoService()
    return await service.import_badge_photos()


@router.post(
    "/badge-photo-attach",
    summary="Создание фотографий из photo_upload бейджей",
    description="Создание записей Photo с фотографиями из поля photo_upload таблицы Badges_2026",
)
async def badge_photo_attach():
    service = BadgePhotoService()
    return await service.attach_badge_photos()
