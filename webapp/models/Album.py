from webapp import Base
from sqlalchemy import CheckConstraint, Column, Integer,String
from sqlalchemy.orm import relationship


class Album(Base):
    """
    A class used to represent an Album

    ...

    Attributes
    ----------
    id : Column
        the id of the album
    name : Column
        the name of the album
    year : Column
        the year of publication of the album
    """

    __tablename__ = "album"

    id  = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    year = Column(Integer, CheckConstraint('year > 1900 and year <= 2022'), nullable=False)
    artists = relationship("AlbumArtist", back_populates="album")
    songs = relationship("Song",cascade="all,delete", back_populates="album")