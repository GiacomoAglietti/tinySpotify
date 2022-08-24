from enum import unique
from webapp import Base
from sqlalchemy import Column, Integer, String, DateTime, event, ForeignKey, DDL, Sequence
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func


class PlaylistSong(Base):
    __tablename__ = "playlist_song"

    id_playlist = Column(Integer, ForeignKey('playlist.id', ondelete="CASCADE"), primary_key=True)
    id_song = Column(Integer, ForeignKey('songs.id', ondelete="CASCADE"), primary_key=True)
    num_in_playlist = Column(Integer) #TODO: da eliminare
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    playlist = relationship("Playlist", back_populates="songs")
    song = relationship("Song", back_populates="playlist")
