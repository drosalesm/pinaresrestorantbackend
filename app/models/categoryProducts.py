from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class CategoryProducts(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)

    # Relationship: A category can have multiple products
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")
