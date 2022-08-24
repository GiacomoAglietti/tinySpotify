from webapp import Base
from sqlalchemy import Column,Integer, String
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

class Genre(Base):
    __tablename__ = "genres"
    name  = Column(String(50), primary_key=True)
    num_of_plays = Column(Integer, default=0)
    song = relationship("Song", backref="genres")