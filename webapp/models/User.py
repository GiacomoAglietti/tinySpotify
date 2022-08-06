from webapp import Base
from sqlalchemy import Column, Integer, String, DateTime, event, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from flask_login import UserMixin
from .Playlist import Playlist

#da mettere in un trigger
#time_updated = Column(DateTime(timezone=True), onupdate=func.now())


class User(Base, UserMixin):   
    __tablename__ = "users"
    id  = Column(Integer, primary_key=True)
    name_surname  = Column(String(150))
    email  = Column(String(150), unique=True)
    password  = Column(String(150))
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    playlist = relationship("Playlist",cascade="all, delete", passive_deletes=True,)

"""
@event.listens_for(User, 'after_attach')
def add_favourite_songs_playlist(session, instance):
    favSongsPlaylist = Playlist(
        id_user = instance.id,
        name = "favourite_songs"
    )
    session.add(favSongsPlaylist)
    session.commit()

    playlist_table = Playlist.__table__
    connection.execute(
        playlist_table.update().
        where(playlist_table.c.id==thread.id).
        values(word_count=sum(c.word_count for c in thread.comments))
    )
"""

@event.listens_for(User, "after_insert")
def after_insert(mapper, connection, target):
    

    newPlaylist = Playlist(
                id_user = target.id, 
                name = "Preferiti")
    target.playlist.append(newPlaylist)

    print ("after insert user -> new favourite song")

