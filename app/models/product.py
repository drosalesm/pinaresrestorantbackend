from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float)
    inventory = Column(Integer, default=0, nullable=True)    
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("CategoryProducts")
