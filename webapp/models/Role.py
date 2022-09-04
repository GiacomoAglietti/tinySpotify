
from webapp import Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

class Role(Base):
    """
    A class used to represent a Role

    ...

    Attributes
    ----------
    name : Column
        the name of the role
    """

    __tablename__ = "roles"

    name = Column(String(50), primary_key=True)
    user = relationship("User", backref="roles")

