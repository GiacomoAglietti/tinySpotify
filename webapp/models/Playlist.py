from webapp import Base
from flask import session
from sqlalchemy import Column, Integer, Boolean, String, event
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from . import User, Song, PlaylistSong, Genre, UserPlaylist

class Playlist(Base):
    __tablename__ = "playlist"
    id  = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    isPremium = Column(Boolean, default=False)
    songs = relationship("PlaylistSong", back_populates="playlist")
    users = relationship("UserPlaylist", back_populates="playlist")    


@event.listens_for(Playlist, "after_insert")
def after_insert(mapper, connection, target):
    
    newUserPlaylist = UserPlaylist(
                id_user = session['userid'], 
                id_playlist = target.id)

    target.album_artist.append(newUserPlaylist)

    print ("insert into UserPlaylist: id_artist=" + session['userid'] + ', id_album=' + target.id)
