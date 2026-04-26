from datetime import datetime

from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.orm import Mapped

from database.meta import Base
from database.orm.base import BaseORM


class SyncStateORM(Base, BaseORM):
    __tablename__ = "sync_state"

    table_name:  Mapped[str] =  Column(String, primary_key=True, nullable=False)
    last_sync: Mapped[datetime] = Column(TIMESTAMP, nullable=False)
