from webapp import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

#da mettere in un trigger
#time_updated = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base):   
    __tablename__ = "users"
    id  = Column(Integer, primary_key=True)
    name_surname  = Column(String(30))
    email  = Column(String(30), unique=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    playlist = relationship("Playlist",cascade="all,delete", back_populates="user")

    def __repr__(self):
        return f"<User id={self.id} name_surname={self.name_surname} email={self.email}>"