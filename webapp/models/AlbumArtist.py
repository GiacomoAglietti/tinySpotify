from webapp import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

class AlbumArtist(Base):
    """
    A class used as association table between Album and User

    ...

    Attributes
    ----------
    id_artist : Column
        foreign key for User table
    id_album : Column
        foreign key for Album table
        
    """

    __tablename__ = "album_artist"

    id_artist = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    id_album = Column(Integer, ForeignKey('album.id', ondelete="CASCADE"), primary_key=True)
    artist = relationship("User", back_populates="album")
    album = relationship("Album", back_populates="artists")
