from webapp import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

class Artist(Base):
    __tablename__ = "artists"
    id  = Column(Integer, primary_key=True)
    alias  = Column(String(30), unique=True)
    name_surname = Column(String(30))
    #TODO da aggiungere trigger che controlla anche le mail degli users
    email  = Column(String(30), unique=True) 
    songs = relationship("Song", secondary="song_artist", back_populates="artists")
    album = relationship("Album", secondary="album_artist", back_populates="artists")
    date_created = Column(DateTime(timezone=True), server_default=func.now())