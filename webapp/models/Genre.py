from webapp import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from . import Song, GenreSong

class Genre(Base):
    __tablename__ = "genres"
    id  = Column(Integer, primary_key=True)
    name = Column(String(150))
    songs = relationship("Song", secondary="genre_song", back_populates="genres")
    date_created = Column(DateTime(timezone=True), server_default=func.now())