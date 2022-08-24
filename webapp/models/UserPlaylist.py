from enum import unique
from webapp import Base
from sqlalchemy import Column, Integer, String, DateTime, event, ForeignKey, DDL, Sequence
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func


class UserPlaylist(Base):
    __tablename__ = "user_playlist"

    id_playlist = Column(Integer, ForeignKey('playlist.id', ondelete="CASCADE"), primary_key=True)
    id_user = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    playlist = relationship("Playlist", back_populates="users", passive_deletes=True)
    user = relationship("User", back_populates="playlist")
