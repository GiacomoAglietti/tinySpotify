from webapp import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin

class User(Base, UserMixin):
    """
    A class used to represent an User

    ...

    Attributes
    ----------
    id : Column
        the id of the user
    name : Column
        the username 
    email : Column
        the email of the user
    passowrd : Column
        the password of the user
    role : Column
        foreign key for Role table
        

    Methods
    -------
    get_role(self)
        Returns the user's role
    """

    __tablename__ = "users"

    id  = Column(Integer, primary_key=True, index=True)
    name  = Column(String(50), unique=True, nullable=False)
    email  = Column(String(50), unique=True, nullable=False)
    password  = Column(String(150), nullable=False)
    role = Column(String(50), ForeignKey('roles.name', ondelete="CASCADE", onupdate="CASCADE"))
    playlist = relationship("UserPlaylist", back_populates="user", passive_deletes=True)
    songs = relationship("SongArtist", back_populates="artist", passive_deletes=True)
    album = relationship("AlbumArtist", back_populates="artist", passive_deletes=True)

    def get_role(self):
            return self.role

