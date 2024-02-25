from sqlalchemy import Column, Date, String
from sqlalchemy.dialects.postgresql import JSONB

from app.db.meta import Base


class PersonORM(Base):
    __tablename__ = "person"

    name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    nickname = Column(String, nullable=True)
    other_names = Column(JSONB, nullable=True)
    gender = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    city = Column(String, nullable=True)
    telegram = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    diet = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    notion_id = Column(String, nullable=False, primary_key=True)

    def __repr__(self):
        return (
            f"Person(name='{self.name}', "
            f"last_name='{self.last_name}', "
            f"first_name='{self.first_name}', "
            f"nickname='{self.nickname}', "
            f"other_names={self.other_names}, "
            f"gender='{self.gender}', "
            f"birth_date={self.birth_date}, "
            f"city='{self.city}', "
            f"telegram='{self.telegram}', "
            f"phone='{self.phone}', "
            f"email='{self.email}', "
            f"diet='{self.diet}', "
            f"comment='{self.comment}', "
            f"notion_id='{self.notion_id}')"
        )
