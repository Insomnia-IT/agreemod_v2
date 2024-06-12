import logging

from typing import Annotated

from fastapi import APIRouter, Depends

from app.db.repos.direction import DirectionRepo
from app.dependencies.db import get_sqla_repo
from app.models.direction import Direction
from app.utils.verify_credentials import verify_credentials


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/directions",
    summary="Список всех служб и локаций",
    response_model=list[Direction],
)
async def get_directions(
    username: Annotated[str, Depends(verify_credentials)],
    repo: DirectionRepo = Depends(get_sqla_repo(DirectionRepo)),
):
    logger.info(f"Starting task: {username}")
    return await repo.retrieve_all()


@router.get(
    "/direction-with-badges",
    summary="Служба с бейджами",
    response_model=Direction,
)
async def get_direction_with_badges(
    notion_id: str,
    username: Annotated[str, Depends(verify_credentials)],
    repo: DirectionRepo = Depends(get_sqla_repo(DirectionRepo)),
):
    logger.info(f"Starting task: {username}")
    return await repo.retrieve(notion_id)
