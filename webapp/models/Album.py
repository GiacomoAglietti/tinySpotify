from webapp import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

class Album(Base):
    __tablename__ = "album"
    id  = Column(Integer, primary_key=True)
    name = Column(String(30))
    year = Column(Integer)
    image = Column(String(50), nullable=True)
    artists = relationship("Artist", secondary="album_artist", back_populates="album")
    songs = relationship("Song",cascade="all,delete", back_populates="album")
    date_created = Column(DateTime(timezone=True), server_default=func.now())