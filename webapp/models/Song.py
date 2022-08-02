from webapp import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from . import Playlist, Genre, Artist, Album, PlaylistSong, GenreSong, SongArtist

class Song(Base):
    __tablename__ = "songs"
    id  = Column(Integer, primary_key=True)
    title = Column(String(150))
    year = Column(Integer)
    length = Column(DateTime(timezone=True)) #TODO: calcolare la durata
    playlist = relationship("Playlist", secondary="playlist_song", back_populates="songs")
    genres = relationship("Genre", secondary="genre_song", back_populates="songs")
    artists = relationship("Artist", secondary="song_artist", back_populates="songs")
    id_album = Column(Integer, ForeignKey("album.id", ondelete="CASCADE"))
    album = relationship("Album", back_populates="songs")
    date_created = Column(DateTime(timezone=True), server_default=func.now())