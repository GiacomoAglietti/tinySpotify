from webapp import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

class SongArtist(Base):
    __tablename__ = "song_artist"

    id_artist = Column(Integer, ForeignKey('artists.id'), primary_key=True)
    id_song = Column(Integer, ForeignKey('songs.id'), primary_key=True)