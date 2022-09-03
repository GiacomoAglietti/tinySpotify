
from webapp import Base
from sqlalchemy import CheckConstraint, Column, Integer,String
from sqlalchemy.orm import relationship

class Role(Base):
    __tablename__ = "roles"

    name = Column(String(50), primary_key=True)
    user = relationship("User", backref="roles")

