from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.orm import Mapped

from db.meta import Base
from app.dictionaries.participation_role import ParticipationRole


class ParticipationRoleORM(Base):
    __tablename__ = "participation_role"

    code: Mapped[str] = Column(String, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    badge_color: Mapped[str] = Column(String, ForeignKey("badge_color.code"))
    is_lead: Mapped[bool] = Column(Boolean, nullable=False)
    is_team: Mapped[bool] = Column(Boolean, nullable=False)
    is_free_feed: Mapped[bool] = Column(Boolean)
    comment: Mapped[str] = Column(String)

    @classmethod
    def fill_table(cls):
        return [
            cls(
                code=x.name,
                name=x.value,
                badge_color=x.badge_color.name,
                is_lead=x.is_lead,
                is_team=x.is_team,
                is_free_feed=x.free_feed,
            )
            for x in ParticipationRole
        ]
