from webapp import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

class Genre(Base):
    __tablename__ = "genres"
    name  = Column(String(50), primary_key=True)
    num_of_plays = Column(Integer, default=0)
    id_playlist = Column(Integer, ForeignKey('playlist.id', ondelete="CASCADE"))
    playlist = relationship("Playlist", backref="genres", uselist=False)
    song = relationship("Song")