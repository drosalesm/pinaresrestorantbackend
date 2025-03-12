from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base
from sqlalchemy.orm import relationship
from app.models.inventory import Inventory  # ✅ Ensure this import is at the bottom
from sqlalchemy.orm import class_mapper


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float)
#    inventory = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="product")  # ✅ Defines the link
