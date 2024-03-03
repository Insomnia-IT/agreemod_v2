# import sys
# sys.path.insert(1, 'C:/Users/ilyam/Documents/Insomnia_integrations/agreemod_v2/agreemod_v2/')

from app.models.badge import Badge
from app.db.meta import Base
from typing import Self
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class BadgeORM(Base):
    """
    infant: признак, что это ребенок
    diet: особенности питания, строка на основе справочника app.dictionaries.diet_type
    feed: платное / бесплатное питание, строка на основе справочника app.dictionaries.feed_type
    role: ForeignKey, строка на основе справочника app.dictionaries.participation_role
    person: ForeignKey, строка на основе таблицы app.models.person
    direction ForeignKey, строка на основе таблицы app.models.direction
    """
        
    __tablename__ = "badge"

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
    role = Column(String, ForeignKey("participation_role."), nullable=False)
    position = Column(String, nullable=True)
    photo = Column(String, nullable=True)
    person = Column(String, ForeignKey("person.notion_id"), nullable=True)
    direction = Column(String, ForeignKey("direction.notion_id"), nullable=True)
    comment = Column(String, nullable=True)
    notion_id = Column(String, nullable=False, primary_key=True)

    @classmethod
    def to_orm(cls, model: Badge) -> Self:
        return cls(
            name=model.name, 
            last_name=model.last_name,  
            first_name=model.first_name,  
            nickname=model.nickname,  
            gender=model.gender,  
            phone=model.phone,  
            infant=model.infant, 
            diet=model.diet, 
            feed=model.feed,  
            number=model.number, 
            batch=model.batch, 
            role=model.role, 
            position=model.position,  
            photo=model.photo,  
            person=model.person,  
            direction=model.direction,  
            comment=model.comment,  
            notion_id=model.notion_id
        )

    def to_model(self) -> Badge:
        return Badge(
            name=self.name, 
            last_name=self.last_name,  
            first_name=self.first_name,  
            nickname=self.nickname,  
            gender=self.gender,  
            phone=self.phone,  
            infant=self.infant, 
            diet=self.diet, 
            feed=self.feed,  
            number=self.number, 
            batch=self.batch, 
            role=self.role, 
            position=self.position,  
            photo=self.photo,  
            person=self.person,  
            direction=self.direction,  
            comment=self.comment,  
            notion_id=self.notion_id            
        )

    def __repr__(self):
        return (
            f"Badge(name='{self.name}', "
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
            f"role='{self.role}', "
            f"position='{self.position}', "
            f"photo='{self.photo}', " 
            f"person='{self.person}', "     
            f"direction='{self.direction}', "
            f"comment='{self.comment}', "
            f"notion_id='{self.notion_id}')"
        )