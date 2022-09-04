from webapp import Base
from sqlalchemy import Column, Integer, Boolean, String
from sqlalchemy.orm import relationship

class Playlist(Base):
    """
    A class used to represent a Playlist

    ...

    Attributes
    ----------
    id : Column
        the id of the playlist
    name : Column
        the name of the playlist
    isPremium : Column
        indicates whether a playlist is premium or not
    """

    __tablename__ = "playlist"

    id  = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    isPremium = Column(Boolean, default=False)
    songs = relationship("PlaylistSong", back_populates="playlist")
    users = relationship("UserPlaylist", back_populates="playlist")