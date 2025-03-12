# schemas/order.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    total: float

    class Config:
        orm_mode = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    customer_name: Optional[str]
    total_price: float
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
            user_id=order.user_id,
            customer_name=order.customer_name,
            total_price=order.total_price,
            status=order.status,
            created_at=order.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
            updated_at=order.updated_at.strftime('%Y-%m-%dT%H:%M:%S'),
            order_items=[OrderItemResponse.from_orm(item) for item in order.order_items]
        )
