from dictionaries.dictionaries import BadgeColor, DirectionType, ParticipationRole
from fastapi import APIRouter, Depends

from app.db.repos.arrival import ArrivalRepo
from app.db.repos.badge import BadgeRepo
from app.dependencies.db import get_sqla_repo
from app.documenters import Q
from app.models.arrival import Arrival
from app.models.badge import Badge
from app.schemas.badge import BadgeFilterDTO


router = APIRouter()


def _get_badges_filters_dto(
    batch: int = Q("Номер партии", None),
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
    filters: BadgeFilterDTO = Depends(_get_badges_filters_dto),
    include_person: bool = False,
    include_directions: bool = False,
    include_infant: bool = False,
    page: int = Q("page", 1, description="page"),
    page_size: int = Q("page size", 10, description="page_size"),
    repo: BadgeRepo = Depends(get_sqla_repo(BadgeRepo)),
):
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
    repo: ArrivalRepo = Depends(get_sqla_repo(BadgeRepo)),
    page: int = Q("page", 1, description="page"),
    page_size: int = Q("page size", 10, description="page_size"),
):
    return await repo.retrieve_all(page=page, page_size=page_size)
