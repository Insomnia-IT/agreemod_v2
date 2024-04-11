from typing import List, Optional

from sqlalchemy.future import select

from app.db.orm import ParticipationAppORM
from app.db.repos.base import BaseSqlaRepo


class ParticipationRepo(BaseSqlaRepo[ParticipationAppORM]):
    async def retrieve_by_person_notion_id(self, person_notion_id: str) -> dict:
        """
        сделал по подобию с PersonRepo, метод не возвращает данные, вопрос к Алексею the-livingstone

        Participation - почему relations не прописаны явно в орм моделе orm.participation.ParticipationORM
        а прописаны тут db.orm.ParticipationAppORM
        """
        results = await self.session.scalars(
            select(ParticipationAppORM).where(
                ParticipationAppORM.notion_id == person_notion_id
            )
        )
        participation = results.all()

        if not participation:
            return None

        return self._orm_to_dict(participation)

    def _orm_to_dict(self, orm_obj):
        # TODO: попросить the-livingstone привести к единому стилю проекта
        if orm_obj is None:
            return None
        orm_model = orm_obj[0]
        return {
            column.key: getattr(orm_model, column.key)
            for column in orm_model.__table__.columns
        }
