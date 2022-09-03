from webapp import Base
from sqlalchemy import Column,Integer, String, ForeignKey, event
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

class Genre(Base):
    __tablename__ = "genres"
    name  = Column(String(50), primary_key=True)
    song = relationship("Song", backref="genres")


    