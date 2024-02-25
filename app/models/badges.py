from pydantic import BaseModel

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Badges(BaseModel):
    """
    infant: признак, что это ребенок - TODO узнать стоит ли сделать автозаполнение на основе даты рождения? Или просто обновляется раз в год при генерации нового бейджа?
    diet: особенности питания, строка на основе справочника app.dictionaries.badges_diet_type
    feed: платное / бесплатное питание, строка на основе справочника app.dictionaries.badges_feed_type
    role: ForeignKey, строка на основе справочника app.dictionaries.participation_role
    person: ForeignKey, строка на основе таблицы app.models.person
    direction ForeignKey, строка на основе таблицы app.models.direction
    """
        
    __tablename__ = "badges"

    name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    nickname = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    infant = Column(Boolean)
    diet = Column(String, nullable=True)
    feed = Column(String, nullable=True)
    number = Column(String, nullable=False)
    batch = Column(Integer, nullable=False)
    # role = Column(String, ForeignKey("participation_role."), nullable=False)
    position = Column(String, nullable=True)
    photo = Column(String, nullable=True)
    # person = Column(String, ForeignKey("person.notion_id"), nullable=True)
    # direction = Column(String, ForeignKey("direction.notion_id"), nullable=True)
    comment = Column(String, nullable=True)
    notion_id = Column(String, nullable=False, primary_key=True)

    def __repr__(self):
        return (
            f"Badges(name='{self.name}', "
            f"last_name='{self.last_name}', "
            f"first_name='{self.first_name}', "
            f"nickname='{self.nickname}', "
            f"gender='{self.gender}', "
            f"phone='{self.phone}', "
            f"infant='{self.infant}', "
            f"diet='{self.diet}', "
            f"feed='{self.feed}', "
            f"number='{self.number}', "
            f"batch='{self.batch}', " 
            # f"role='{self.role}', "
            f"position='{self.position}', "
            f"photo='{self.photo}', " 
            # f"person='{self.person}', "     
            # f"direction='{self.direction}', "
            f"comment='{self.comment}', "
            f"notion_id='{self.notion_id}')"
        )