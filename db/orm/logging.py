from sqlalchemy import Column, Integer, String, TIMESTAMP, JSON
from sqlalchemy.orm import Mapped

from db.meta import Base
from db.orm.base import BaseORM


class LogsORM(Base, BaseORM):
    """
    id: unique identifier for each log entry
    author: name of the user who performed the operation
    table_name: name of the table where the operation occurred
    operation: type of operation performed (e.g., INSERT, UPDATE, DELETE)
    timestamp: the time when the operation was performed
    new_data: JSON containing the new state of the data after the operation
    """

    __tablename__ = "logs"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    author: Mapped[str] = Column(String, nullable=True)
    table_name: Mapped[str] = Column(String, nullable=False)
    row_id: Mapped[str] = Column(String, nullable=False)
    operation: Mapped[str] = Column(String, nullable=False)
    timestamp: Mapped[TIMESTAMP] = Column(TIMESTAMP, nullable=False)
    new_data: Mapped[JSON] = Column(JSON)

    @classmethod
    def bake(self):
        pass

    def __repr__(self):
        return (
            f"AuditLog(id={self.id}, author='{self.author}', "
            f"table_name='{self.table_name}', row_id={self.row_id}, "
            f"operation='{self.operation}', timestamp={self.timestamp}, "
            f"new_data={self.new_data})"
        )
