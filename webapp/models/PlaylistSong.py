from webapp import Base
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class PlaylistSong(Base):
    """
    A class used as association table between Playlist and Song

    ...

    Attributes
    ----------
    id_playlist : Column
        foreign key for Playlist table
    id_song : Column
        foreign key for Song table
    date_created: Column
        indicates when a song has been added into a playlist
        
    """

    __tablename__ = "playlist_song"

    id_playlist = Column(Integer, ForeignKey('playlist.id', ondelete="CASCADE"), primary_key=True)
    id_song = Column(Integer, ForeignKey('songs.id', ondelete="CASCADE"), primary_key=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    playlist = relationship("Playlist", back_populates="songs", passive_deletes=True)
    song = relationship("Song", back_populates="playlist")
