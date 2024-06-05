import os
import time
import zipfile

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from app.db.repos.arrival import ArrivalRepo
from app.db.repos.badge import BadgeRepo
from app.dependencies.db import get_sqla_repo
from app.documenters import Q
from app.models.arrival import Arrival
from app.models.badge import Badge

router = APIRouter()


@router.get(
    "/badges",
    summary="Бейджи",
    response_model=list[Badge],
)
async def get_badges(
    repo: BadgeRepo = Depends(get_sqla_repo(BadgeRepo)),
    page: int = Q("page", 1, description="page"),
    page_size: int = Q("page size", 10, description="page_size"),
):
    return await repo.retrieve_all(page=page, page_size=page_size)


@router.get(
    "/arrivals",
    summary="Заезды",
    response_model=list[Arrival],
)
async def get_arrivals(
    repo: ArrivalRepo = Depends(get_sqla_repo(BadgeRepo)),
    page: int = Q("page", 1, description="page"),
    page_size: int = Q("page size", 10, description="page_size"),
):
    return await repo.retrieve_all(page=page, page_size=page_size)


ARCHIVE_NAME = "archive.zip"
TEXT_FILE_NAME = "hello.txt"


def create_zip_file():
    time.sleep(5)  # Имитация долгой задачи
    with zipfile.ZipFile(ARCHIVE_NAME, 'w') as zipf:

        # Создание временного текстового файла
        with open(TEXT_FILE_NAME, 'w') as file:
            file.write("Hello World")

        # Добавление текстового файла в архив
        zipf.write(TEXT_FILE_NAME)

        # Удаление временного текстового файла после добавления в архив
        os.remove(TEXT_FILE_NAME)


@router.post("/start-task/")
async def start_task(background_tasks: BackgroundTasks):
    """
    Создание задачи на создание .zip файла со всеми данными
    """
    background_tasks.add_task(create_zip_file)
    return {"message": "Фоновая задача по созданию архива запущена"}


@router.get("/download-archive/")
async def download_archive():
    """
    Возвращает файл который подготовил /start-task эндпоинт
    """
    if os.path.exists(ARCHIVE_NAME):
        return FileResponse(path=ARCHIVE_NAME, media_type='application/zip', filename=ARCHIVE_NAME)
    else:
        raise HTTPException(status_code=404, detail="Архив не найден")
