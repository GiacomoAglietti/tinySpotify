from webapp import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

class GenreSong(Base):
    __tablename__ = "genre_song"

    id_genre = Column(Integer, ForeignKey('genres.id', ondelete="CASCADE"), primary_key=True)
    id_song = Column(Integer, ForeignKey('songs.id', ondelete="CASCADE"), primary_key=True)
    genre = relationship("Genre", back_populates="songs")
    song = relationship("Song", back_populates="genres")