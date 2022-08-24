from webapp import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

class AlbumArtist(Base):
    __tablename__ = "album_artist"

    id_artist = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    id_album = Column(Integer, ForeignKey('album.id', ondelete="CASCADE"), primary_key=True)
    artist = relationship("User", back_populates="album")
    album = relationship("Album", back_populates="artists")
