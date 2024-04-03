from fastapi import APIRouter, Depends

from app.db.repos.badge import BadgeRepo
from app.dependencies.db import get_sqla_repo
from app.models.badge import Badge
from app.documenters import Q

router = APIRouter()


@router.get(
    "/badges",
    summary="Бейджи",
    response_model=list[Badge],
)
async def get_badges(
        repo: BadgeRepo = Depends(get_sqla_repo(BadgeRepo)),
        page: int = Q("page", 1, description="page"),
        page_size: int = Q("page size", 10, description="page_size"), ):
    return await repo.retrieve_all(page=page, page_size=page_size)
