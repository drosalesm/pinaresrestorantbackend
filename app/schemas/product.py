from pydantic import BaseModel
from typing import List, Optional


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: Optional[int] = None  # Allow updating category_id


# ✅ Schema for updating a product
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    category_id: Optional[int] = None  # Include category_id as an optional field


# Enables ORM support

class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True
    
class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float

    class Config:
        orm_mode = True