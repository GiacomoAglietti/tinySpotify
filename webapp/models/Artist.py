from webapp import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from flask_login import UserMixin
from . import Song, Album, SongArtist, AlbumArtist

class Artist(Base, UserMixin):
    __tablename__ = "artists"
    id  = Column(Integer, primary_key=True)
    alias  = Column(String(150), unique=True)
    name_surname = Column(String(150))
    #TODO da aggiungere trigger che controlla anche le mail degli users
    email  = Column(String(150), unique=True)
    password  = Column(String(150))
    songs = relationship("SongArtist", back_populates="artist")

    album = relationship("AlbumArtist", back_populates="artist")
    date_created = Column(DateTime(timezone=True), server_default=func.now())


