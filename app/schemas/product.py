from pydantic import BaseModel
from typing import List, Optional


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    imageUrl: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: Optional[int] = None  # Allow updating category_id
    inventory: Optional[int] = None  # Allow updating category_id    
    imageUrl: Optional[str] = None
    unidad_de_negocio: Optional[str] = None  

# ✅ Schema for updating a product
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    category_id: Optional[int] = None  # Include category_id as an optional field
    inventory: Optional[int] = None
    imageUrl: Optional[str] = None
    unidad_de_negocio: Optional[str] = None  

    class Config:
        orm_mode = True  # Enables ORM support

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
    unidad_de_negocio: Optional[str] = None
    
    class Config:
        orm_mode = True