from webapp import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from . import User, Song, PlaylistSong, Genre

class Playlist(Base):
    __tablename__ = "playlist"
    id  = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    isPremium = Column(Boolean, default=False)
    id_user = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    songs = relationship("PlaylistSong", back_populates="playlist")    
