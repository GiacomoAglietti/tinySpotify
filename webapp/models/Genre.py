from webapp import Base
from sqlalchemy import Column,Integer, String, ForeignKey, event
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

from webapp.models.Playlist import Playlist

class Genre(Base):
    __tablename__ = "genres"
    name  = Column(String(50), primary_key=True)
    id_playlist = Column(Integer, ForeignKey("Playlist.id"), ondelete="CASCADE", onupdate="CASCADE")
    song = relationship("Song", backref="genres")


    