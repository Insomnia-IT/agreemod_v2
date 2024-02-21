from fastapi import APIRouter, Depends

from app.db.repos.direction import DirectionRepo
from app.db.repos.person import PersonRepo
from app.dependencies.db import get_sqla_repo
from app.documenters import Q
from app.main import api_router
from app.schemas.direction import DirectionResponseSchema


router = APIRouter()


@router.get(
    "/directions",
    summary="Список всех служб и локаций",
    response_model=list[DirectionResponseSchema],
)
async def get_directions(
    order_by: str = Q("Поле сортировки", "nickname"),
    repo: DirectionRepo = Depends(get_sqla_repo(DirectionRepo)),
):
    return await repo.retrieve_many(order_by)


api_router.include_router(router)
