from fastapi import APIRouter, Depends

from app.db.repos.person import PersonRepo
from app.dependencies.db import get_sqla_repo
from app.documenters import Q
from app.main import api_router
from app.schemas.person import PersonFiltersDTO, PersonResponseSchema


router = APIRouter(prefix="/agreemod")


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
    "/contacts/search",
    summary="Поиск в базе контактов оргов и волонтёров",
    response_model=list[PersonResponseSchema],
)
async def get_orgs_and_volunteers(
    filters: PersonFiltersDTO = Depends(_get_person_filters_dto),
    order_by: str = Q("Поле сортировки", "nickname"),
    repo: PersonRepo = Depends(get_sqla_repo(PersonRepo)),
):
    return await repo.retrieve_many(filters, order_by)


api_router.include_router(router)
