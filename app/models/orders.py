from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
from app.utils.timezone_config import get_current_local_time



class billingConfig(Base):
    __tablename__ = "billingConfig"

    id = Column(Integer, primary_key=True, index=True)
    isv =Column(Integer, nullable=True)  


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
#    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    username= Column(String, nullable=True)
    customer_name = Column(String, nullable=True)
    total_price = Column(Float, nullable=False)
    isv =Column(Float, nullable=True)  
    final_price = Column(Float, nullable=True)
    status = Column(String, default="pending")  # e.g., 'pending', 'shipped', 'delivered'
    created_at = Column(DateTime, default=get_current_local_time)
    updated_at = Column(DateTime, default=get_current_local_time, onupdate=get_current_local_time)

#    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def update_total_price(self):
        self.total_price = sum(item.total for item in self.order_items)

        
        
        

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    total = Column(Float, nullable=False)  # This could be price * quantity

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")
