from app.database import Base
from sqlalchemy import Column,  String, URL,Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from typing import Dict,List

class URL(Base):
    __tablename__ = 'urls'

    id = Column(Integer,primary_key=True,unique=True)
    original_url = Column(Text,index=True,nullable=False)
    short_code = Column(String(8),unique=True,nullable=False)
    clicks = Column(Integer,default=0)
    description = Column(Text,nullable= True)

    visits = relationship("Visit",back_populates="url",cascade='all, delete')

    def __repr__(self):
        return f'link: {self.original_url} | short: {self.short_code}'



class Visit(Base):
    __tablename__ = 'visits'

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id",ondelete='CASCADE'),index=True)
    timestamp = Column(DateTime, default=datetime.now)

    ip = Column(String)
    referrer = Column(String)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    agent = Column(String, nullable=True)


    url = relationship("URL", back_populates="visits")



class URLSCHEMA(BaseModel):
    id : int
    original_url : str 
    short_code : str
    clicks : int
    description : str | None = None


class CreateCode(BaseModel):
    url : str
    description : str | None = None



class VisitSchema(BaseModel):
    id : int
    url_id : int
    timestamp : datetime

    ip : str
    referrer : str | None = None
    country : str
    city : str
    agent : str

    class Meta:
        from_attributes = True




class ShortStats(BaseModel):
    visits_per_day: List[Dict[datetime, int]]
    all_visits: List[VisitSchema]