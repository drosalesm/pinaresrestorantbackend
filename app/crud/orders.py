# crud/order.py
from sqlalchemy.orm import Session
from app.models.orders import Order
from app.schemas.orders import OrderResponse

def get_orders(db: Session, user_id: int):
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    return [OrderResponse.from_orm(order) for order in orders]  # Serialize response

def get_order_by_id(db: Session, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        return OrderResponse.from_orm(order)
    return None  # Return None if order doesn't exist
