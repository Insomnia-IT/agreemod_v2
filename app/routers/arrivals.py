from fastapi import APIRouter, Depends

from app.dependencies.db import get_sqla_repo
from app.documenters import Q

from app.db.repos.arrival import ArrivalRepo
from app.models.arrival import Arrival

router = APIRouter()


@router.get(
    "/arrivals",
    summary="Заезды",
    response_model=list[    ],
)
async def get_arrivals(
        repo: ArrivalRepo = Depends(get_sqla_repo(ArrivalRepo)),
        page: int = Q("page", 1, description="page"),
        page_size: int = Q("page size", 10, description="page_size"), ):
    return await repo.retrieve_all(page=page, page_size=page_size)