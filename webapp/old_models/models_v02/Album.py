from typing import Concatenate
from webapp import Base
from sqlalchemy import CheckConstraint, Column, Integer,String
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

class Album(Base):
    __tablename__ = "album"

    id  = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    year = Column(Integer, CheckConstraint('year > 1900 and year <= 2022'), nullable=False)
    image = Column(String(100))
    artists = relationship("AlbumArtist", back_populates="album")
    songs = relationship("Song",cascade="all,delete", back_populates="album")

