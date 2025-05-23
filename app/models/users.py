from sqlalchemy import Column, Integer, String
from app.db.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    name= Column(String, nullable=True)
    email = Column(String, nullable=True)
    hashed_password = Column(String)
    role = Column(String, default="user") 
    
#    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")