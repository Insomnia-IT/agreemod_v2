from fastapi import APIRouter, Depends

from app.db.repos.direction import DirectionRepo
from app.dependencies.db import get_sqla_repo
from app.models.direction import Direction


router = APIRouter()


@router.get(
    "/directions",
    summary="Список всех служб и локаций",
    response_model=list[Direction],
)
async def get_directions(repo: DirectionRepo = Depends(get_sqla_repo(DirectionRepo))):
    return await repo.retrieve_all()
