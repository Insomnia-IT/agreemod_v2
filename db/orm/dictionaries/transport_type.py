from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped

from db.meta import Base


class TransportTypeORM(Base):
    __tablename__ = "transport_type"

    code: Mapped[str] = Column(String, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    comment: Mapped[str] = Column(String)
