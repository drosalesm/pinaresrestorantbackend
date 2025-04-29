# schemas/order.py
from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel, condecimal
from typing import Optional, Dict



class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    total: float

    class Config:
        orm_mode = True

class OrderResponse(BaseModel):
    id: int
    username: str
    customer_name: Optional[str]
    total_price: float
    isv: Optional[float] = None
    final_price: Optional[float] = None
    status: str
    created_at: str  # Convert to string format
    updated_at: str  # Convert to string format
    order_items: List[OrderItemResponse]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, order):
        return cls(
            id=order.id,
            username=order.username,
            customer_name=order.customer_name,
            total_price=order.total_price,
            isv=order.isv,
            final_price=order.final_price,
            status=order.status,
            created_at=order.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
            updated_at=order.updated_at.strftime('%Y-%m-%dT%H:%M:%S'),
            order_items=[OrderItemResponse.from_orm(item) for item in order.order_items]
        )



        


class OrderItemCreateSchema(BaseModel):
    product_id: int
    quantity: int  # Simplified to just int
    total: float  # Simplified to just float

    class Config:
        orm_mode = True

class OrderCreateSchema(BaseModel):
    username: str
    customer_name: Optional[str] = None  # Optional field
    status: str = "pending"  # Default status
    order_items: List[OrderItemCreateSchema]  # List of items in the order

    class Config:
        orm_mode = True
        
        
        



class OrderItemUpdateSchema(BaseModel):
    product_id: int
    quantity: int  # Must be positive (validate in service logic)
    total: float   # Must be positive (validate in service logic)

class OrderUpdateSchema(BaseModel):
    customer_name: Optional[str] = None
    status: Optional[str] = None
    order_items: Optional[List[OrderItemUpdateSchema]] = None  # Optional

    class Config:
        orm_mode = True
        
        
class ProductReport(BaseModel):
    product_name: str
    total_sales: int
    total_amount: float

    class Config:
        orm_mode = True  # This allows Pydantic to work directly with ORM models