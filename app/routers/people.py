import logging

from typing import Annotated

from fastapi import APIRouter, Depends

from app.db.repos.participation import ParticipationRepo
from app.db.repos.person import PersonRepo
from app.dependencies.db import get_sqla_repo
from app.documenters import Q
from app.models.participation import Participation
from app.models.person import Person
from app.schemas.person import PersonFiltersDTO, PersonResponseSchema, TelebotResponseSchema
from app.utils.verify_credentials import verify_credentials


router = APIRouter()
logger = logging.getLogger(__name__)


def _get_person_filters_dto(
    telegram: str | None = Q("Ник в Телеграм", None),
    phone_number: str | None = Q("Номер телефона", None),
    email: str | None = Q("Почта", None),
    strict: bool = False,
) -> PersonFiltersDTO:
    return PersonFiltersDTO(
        telegram=telegram,
        phone=phone_number,
        email=email,
        strict=strict,
    )


@router.get(
    "/persons",
    summary="Человеки",
    response_model=list[Person],
)
async def get_persons(
    username: Annotated[str, Depends(verify_credentials)],
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
    username: Annotated[str, Depends(verify_credentials)],
    filters: PersonFiltersDTO = Depends(_get_person_filters_dto),
    order_by: str = Q("Поле сортировки", "nickname"),
    limit: int = Q("Количество записей на одной странице", 20),
    offset: int = Q("Смещение от начала", 0),
    repo: PersonRepo = Depends(get_sqla_repo(PersonRepo)),
):
    return await repo.retrieve_many(filters, order_by, limit, offset)


@router.get(
    "/contacts/search",
    summary="Человеки",
    response_model=TelebotResponseSchema | None,
)
async def get_telebot_person(
    username: Annotated[str, Depends(verify_credentials)],
    telegram: str,
    repo: PersonRepo = Depends(get_sqla_repo(PersonRepo)),
    repo_part: ParticipationRepo = Depends(get_sqla_repo(ParticipationRepo)),
):
    """
    API для работы с телеграм ботом по промокодам
    https://github.com/Insomnia-IT/promocode_bot
    """
    person = await repo.retrieve(None, PersonFiltersDTO(telegram=telegram, strict=True))
    if not person:
        person = await repo.retrieve(None, PersonFiltersDTO(telegram="@" + telegram, strict=True))
    if not person:
        return None
    participations = await repo_part.retrieve_personal(str(person.notion_id), True)

    roles = [i.role.lower() for i in participations if i.role]
    organiser = "организатор" in roles
    person_for_telebot = TelebotResponseSchema(
        uuid=person.notion_id,
        nickname=person.nickname,
        lastname=person.last_name,
        name=person.name,
        telegram=person.telegram,
        email=person.email,
        second_email=person.email,
        phone_number=person.phone,
        role="организатор" if organiser else "волонтёр",
        volunteer=roles,
        organize=roles,
    )
    return person_for_telebot


@router.get(
    "/participation",
    summary="Участие",
    response_model=list[Participation],
)
async def get_participation(
    username: Annotated[str, Depends(verify_credentials)],
    repo: ParticipationRepo = Depends(get_sqla_repo(ParticipationRepo)),
    page: int = Q("page", 1, description="page"),
    page_size: int = Q("page size", 10, description="page_size"),
):
    logger.info(f"Starting task: {username}")
    return await repo.retrieve_all(page=page, page_size=page_size)
