from enum import unique
from webapp import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

class PlaylistSong(Base):
    __tablename__ = "playlist_song"

    id_playlist = Column(Integer, ForeignKey('playlist.id'), primary_key=True)
    id_song = Column(Integer, ForeignKey('songs.id'), primary_key=True)
    num_order = Column(Integer)
    
    
