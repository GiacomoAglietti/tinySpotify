from webapp import Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

class Genre(Base):
    """
    A class used to represent a Genre

    ...

    Attributes
    ----------
    name : Column
        the name of the genre
    """

    __tablename__ = "genres"
    
    name  = Column(String(50), primary_key=True)
    song = relationship("Song", backref="genres")


    