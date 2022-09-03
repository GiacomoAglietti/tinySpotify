from typing import Concatenate
from flask import session
from webapp import Base
from sqlalchemy import CheckConstraint, Column, Integer,String, event
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from .AlbumArtist import AlbumArtist

class Album(Base):
    __tablename__ = "album"

    id  = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    year = Column(Integer, CheckConstraint('year > 1900 and year <= 2022'), nullable=False)
    artists = relationship("AlbumArtist", back_populates="album")
    songs = relationship("Song",cascade="all,delete", back_populates="album")
"""
@event.listens_for(Album, "after_insert")
def after_insert(mapper, connection, target):
    
    newAlbumArtist = AlbumArtist(
                id_artist = session['userid'], 
                id_album = target.id)

    target.album_artist.append(newAlbumArtist)

    print ("insert into AlbumArtist: id_artist=" + session['userid'] + ', id_album=' + target.id)
"""