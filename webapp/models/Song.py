from webapp import Base
from sqlalchemy import CheckConstraint, Column, Integer,ForeignKey,DateTime,String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func



class Song(Base):
    """
    A class used to represent a Playlist

    ...

    Attributes
    ----------
    id : Column
        the id of the playlist
    title : Column
        the name of the playlist
    year : Column
        indicates whether a playlist is premium or not
    length : Column
        the id of the playlist
    num_of_plays : Column
        the name of the playlist
    date_created : Column
        indicates whether a playlist is premium or not
    id_album : Column
        the id of the playlist
    genre : Column
        the name of the playlist
    """

    __tablename__ = "songs"

    __table_args__ = (UniqueConstraint('title', 'id_album', name='title_id_album'),)

    id  = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    year = Column(Integer, CheckConstraint('year > 1900 and year <= 2022'), nullable=False)
    length = Column(Integer, CheckConstraint('length > 0 and length < 3600'), nullable=False)
    num_of_plays = Column(Integer, default=0)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    id_album = Column(Integer, ForeignKey("album.id", ondelete="CASCADE"))
    genre = Column(String(50), ForeignKey('genres.name', ondelete="CASCADE", onupdate="CASCADE"))
    album = relationship("Album", back_populates="songs")
    playlist = relationship("PlaylistSong", back_populates="song")
    artists = relationship("SongArtist", back_populates="song")    
    