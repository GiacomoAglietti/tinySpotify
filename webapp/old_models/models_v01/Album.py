from webapp import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

class Album(Base):
    __tablename__ = "album"
    id  = Column(Integer, primary_key=True)
    name = Column(String(150))
    year = Column(Integer)
    image = Column(String(150), nullable=True)
    artists = relationship("AlbumArtist", back_populates="album")
    songs = relationship("Song",cascade="all,delete", back_populates="album")