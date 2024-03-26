from fastapi import APIRouter, Depends

from app.db.repos.person import PersonRepo
from app.dependencies.db import get_sqla_repo
from app.documenters import Q
from app.models.person import Person
from app.schemas.person import PersonFiltersDTO, PersonResponseSchema


router = APIRouter()


def _get_person_filters_dto(
    telegram: str | None = Q("Ник в Телеграм", None),
    phone_number: str | None = Q("Номер телефона", None),
    email: str | None = Q("Почта", None),
) -> PersonFiltersDTO:
    return PersonFiltersDTO(
        telegram=telegram,
        phone_number=phone_number,
        email=email,
    )


@router.get(
    "/persons",
    summary="Человеки",
    response_model=list[Person],
)
async def get_persons(
    repo: PersonRepo = Depends(get_sqla_repo(PersonRepo)),
    page: int = Q("page", 1, description="page"),
    page_size: int = Q("page size", 10, description="page_size"),
):
    return await repo.retrieve_all(page=page, page_size=page_size)


@router.get(
    "/contacts",
    summary="Поиск в базе контактов оргов и волонтёров",
    response_model=list[PersonResponseSchema],
)
async def get_orgs_and_volunteers(
    filters: PersonFiltersDTO = Depends(_get_person_filters_dto),
    order_by: str = Q("Поле сортировки", "nickname"),
    limit: int = Q("Количество записей на одной странице", 20),
    offset: int = Q("Смещение от начала", 0),
    repo: PersonRepo = Depends(get_sqla_repo(PersonRepo)),
):
    return await repo.retrieve_many(filters, order_by, limit, offset)
