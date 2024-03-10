from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped

from app.db.meta import Base
from app.dictionaries.transport_type import TransportType


class TransportTypeORM(Base):
    __tablename__ = "transport_type"

    code: Mapped[str] = Column(String, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    comment: Mapped[str] = Column(String)

    @classmethod
    def fill_table(cls):
        return [
            cls(
                code=x.name,
                name=x.value,
            )
            for x in TransportType
        ]
