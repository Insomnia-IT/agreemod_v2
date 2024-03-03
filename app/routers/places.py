from fastapi import APIRouter, Depends

from app.db.repos.direction import DirectionRepo
from app.db.repos.person import PersonRepo
from app.dependencies.db import get_sqla_repo
from app.documenters import Q
from app.main import api_router
from app.models.direction import Direction
from app.schemas.direction import DirectionResponseSchema

router = APIRouter()


@router.get(
    "/directions",
    summary="Список всех служб и локаций",
    response_model=list[Direction],
)
async def get_directions(
        repo: DirectionRepo = Depends(get_sqla_repo(DirectionRepo))
):
    return await repo.retrieve_all()


api_router.include_router(router)
