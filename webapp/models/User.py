from webapp import Base
from sqlalchemy import Column, Integer, String, DateTime, event, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from flask_login import UserMixin
from webapp.models.Playlist import Playlist

#da mettere in un trigger
#time_updated = Column(DateTime(timezone=True), onupdate=func.now())


class User(Base, UserMixin):   
    __tablename__ = "users"

    id  = Column(Integer, primary_key=True, index=True)
    name  = Column(String(50), unique=True, nullable=False)
    email  = Column(String(50), unique=True, nullable=False)
    password  = Column(String(150), nullable=False)
    role = Column(String(50), ForeignKey('roles.name', ondelete="CASCADE", onupdate="CASCADE"))
    playlist = relationship("UserPlaylist", back_populates="user", passive_deletes=True)
    songs = relationship("SongArtist", back_populates="artist", passive_deletes=True)
    album = relationship("AlbumArtist", back_populates="artist", passive_deletes=True)

    def get_role(self):
            return self.role

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
"""
@event.listens_for(User, "after_insert")
def after_insert(mapper, connection, target):
    

    newPlaylist = Playlist(
                name = "Preferiti")
    target.playlist.append(newPlaylist)

    print ("after insert user -> new favourite song")
"""

