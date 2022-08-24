from email.policy import default
from webapp import Base
from sqlalchemy import CheckConstraint, Column, Integer,ForeignKey,DateTime,String
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from . import Playlist, Genre, Album, PlaylistSong, SongArtist



class Song(Base):
    __tablename__ = "songs"

    id  = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    year = Column(Integer, CheckConstraint('year > 1900 and year <= 2022'), nullable=False)
    length = Column(Integer, CheckConstraint('length > 0 and length < 3600 '), nullable=False)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    id_album = Column(Integer, ForeignKey("album.id", ondelete="CASCADE"))
    genre = Column(String(50), ForeignKey('genres.name', ondelete="CASCADE", onupdate="CASCADE"))
    album = relationship("Album", back_populates="songs")
    playlist = relationship("PlaylistSong", back_populates="song")
    artists = relationship("SongArtist", back_populates="song")
    
    

    """
    from integer to hour
    Hour = int(value / 3600)
    Min  = int(value % 3600 / 60)
    Sec  = value % 3600 % 1800

    from hour to integer
    hour = 0
    min = 4
    sec = 5        
    len = sec + min * 60 + hour * 3600
    """