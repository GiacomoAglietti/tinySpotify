from email.policy import default
from webapp import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from . import Playlist, Genre, Album, PlaylistSong, GenreSong, SongArtist



class Song(Base):
    __tablename__ = "songs"
    id  = Column(Integer, primary_key=True)
    title = Column(String(150))
    year = Column(Integer)
    length = Column(Integer)
    num_in_album = Column(Integer)
    id_album = Column(Integer, ForeignKey("album.id", ondelete="CASCADE"))
    album = relationship("Album", back_populates="songs")
    playlist = relationship("PlaylistSong", back_populates="song")
    genres = relationship("GenreSong", back_populates="song")
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