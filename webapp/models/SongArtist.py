from webapp import Base
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

class SongArtist(Base):
    """
    A class used as association table between Song and User

    ...

    Attributes
    ----------
    id_song : Column
        foreign key for Song table
    id_artist : Column
        foreign key for User table
        
    """

    __tablename__ = "song_artist"

    id_artist = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    id_song = Column(Integer, ForeignKey('songs.id', ondelete="CASCADE"), primary_key=True)
    artist = relationship("User", back_populates="songs")
    song = relationship("Song", back_populates="artists")