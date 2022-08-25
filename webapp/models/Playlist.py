from webapp import Base
from flask import session
from sqlalchemy import Column, Integer, Boolean, String, event
from sqlalchemy import insert
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from . import User, Song, PlaylistSong, Genre
from webapp.models.UserPlaylist import UserPlaylist
from webapp import db_session

local_session = db_session()


class Playlist(Base):
    __tablename__ = "playlist"
    id  = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    isPremium = Column(Boolean, default=False)
    songs = relationship("PlaylistSong", back_populates="playlist")
    users = relationship("UserPlaylist", back_populates="playlist")    


@event.listens_for(Playlist, "after_insert")
def after_insert(mapper, connection, target):

    stmt = (insert(UserPlaylist).
            values(id_playlist = target.id).
            values(id_user = session['userid']))

    connection.execute(stmt)
    local_session.commit()

    print ("insert into UserPlaylist: id_artist=" + str(session['userid']) + ', id_album=' + str(target.id))

