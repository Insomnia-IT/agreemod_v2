import logging
import os

from typing import Annotated

from dictionaries.dictionaries import BadgeColor, DirectionType, ParticipationRole
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse

from app.db.repos.arrival import ArrivalRepo
from app.db.repos.badge import BadgeRepo
from app.dependencies.db import get_sqla_repo
from app.dependencies.service import get_badge_service
from app.documenters import Q
from app.models.arrival import Arrival
from app.models.badge import Badge
from app.schemas.badge import BadgeFilterDTO
from app.services.badge import BadgeService
from app.utils.verify_credentials import verify_credentials


router = APIRouter()
logger = logging.getLogger(__name__)


def _get_badges_filters_dto(
    batch: int | None = Q("Номер партии", None),
    color: BadgeColor | None = Q("Цвет бейджа", None),
    direction: DirectionType | None = Q("Название службы (направления)", None),
    role: ParticipationRole | None = Q("Роль", None),
    occupation: str = Q("Тип участия", None),
    infants: str | None = Q("Найти детей по notion_id бейджа родителя", None),
) -> BadgeFilterDTO:
    return BadgeFilterDTO(
        batch=batch,
        color=color,
        direction=direction,
        role=role,
        occupation=occupation,
        infants=infants,
    )


@router.get(
    "/badges",
    summary="Бейджи",
    response_model=list[Badge],
)
async def get_badges(
    username: Annotated[str, Depends(verify_credentials)],
    filters: BadgeFilterDTO = Depends(_get_badges_filters_dto),
    include_person: bool = False,
    include_directions: bool = False,
    include_infant: bool = False,
    page: int = Q("page", 1, description="page"),
    page_size: int = Q("page size", 10, description="page_size"),
    repo: BadgeRepo = Depends(get_sqla_repo(BadgeRepo)),
):
    logger.info(f"Starting task: {username}")
    return await repo.retrieve_many(
        page=page,
        page_size=page_size,
        filters=filters,
        include_person=include_person,
        include_directions=include_directions,
        include_infant=include_infant,
    )


@router.get(
    "/arrivals",
    summary="Заезды",
    response_model=list[Arrival],
)
async def get_arrivals(
    username: Annotated[str, Depends(verify_credentials)],
    repo: ArrivalRepo = Depends(get_sqla_repo(ArrivalRepo)),
    page: int = Q("page", 1, description="page"),
    page_size: int = Q("page size", 10, description="page_size"),
):
    logger.info(f"Starting task: {username}")
    return await repo.retrieve_all(page=page, page_size=page_size)


ARCHIVE_NAME = "archive.zip"
TEXT_FILE_NAME = "hello.txt"


# def create_zip_file():
#     time.sleep(5)  # Имитация долгой задачи
#     with zipfile.ZipFile(ARCHIVE_NAME, 'w') as zipf:
#         # Создание временного текстового файла
#         with open(TEXT_FILE_NAME, 'w') as file:
#             file.write("Hello World")

#         # Добавление текстового файла в архив
#         zipf.write(TEXT_FILE_NAME)

#         # Удаление временного текстового файла после добавления в архив
#         os.remove(TEXT_FILE_NAME)


@router.post("/prepare-badges/")
async def start_task(
    username: Annotated[str, Depends(verify_credentials)],
    background_tasks: BackgroundTasks,
    batch: int,
    service: BadgeService = Depends(get_badge_service),
):
    """
    Создание задачи на создание .zip файла со всеми данными
    """
    logger.info(f"Starting task: {username}")
    background_tasks.add_task(service.prepare_to_print, batch)
    return {"message": "Фоновая задача по созданию архива запущена"}


@router.get("/download-archive/")
async def download_archive(username: Annotated[str, Depends(verify_credentials)], batch: int):
    """
    Возвращает файл который подготовил /start-task эндпоинт
    """
    logger.info(f"Starting task: {username}")
    if os.path.exists(f"batch_{batch}.zip"):
        return FileResponse(
            path=f"batch_{batch}.zip",
            media_type="application/zip",
            filename=f"batch_{batch}.zip",
        )
    else:
        raise HTTPException(status_code=404, detail="Архив не найден")


@router.get("/get-anonymous-badges")
async def get_anons(
    username: Annotated[str, Depends(verify_credentials)],
    batch: str,
    service: BadgeService = Depends(get_badge_service),
):
    await service.prepare_anonymous(batch)
    if os.path.exists(f"batch_{batch}.zip"):
        return FileResponse(
            path=f"batch_{batch}.zip",
            media_type="application/zip",
            filename=f"batch_{batch}.zip",
        )
    else:
        raise HTTPException(status_code=404, detail="Архив не найден")
