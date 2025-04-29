# crud/order.py
from sqlalchemy.orm import Session
from app.models.orders import Order,OrderItem,billingConfig
from app.models.product import Product
from app.schemas.orders import OrderResponse,OrderCreateSchema,OrderUpdateSchema,ProductReport
from datetime import datetime
from app.models.users import User
from sqlalchemy import func
from typing import Optional
from app.utils.utils import serialize_product_report
from sqlalchemy.sql.expression import extract


def get_orders(db: Session, user_id: int):
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    return [OrderResponse.from_orm(order) for order in orders]  # Serialize response



def get_order_by_id(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()




def create_order(db: Session, order_data: OrderCreateSchema):
    # Ensure user exists

    try:

        isv = db.query(billingConfig).filter(billingConfig.id == 1).first()

        if isv or isv>0:
            isv = isv.isv/100
        else:
            isv = 0
            isv_value=0  


        new_order = Order(
            username=order_data.username,
            customer_name=order_data.customer_name,
            total_price=0,  # Will be updated after adding items
            final_price=0,  # Will be updated after adding items
            isv=isv,  # Use ISV from billingConfig
            status=order_data.status,  # Use provided status
            created_at=datetime.utcnow(),
            updated_at=None,
        )

        db.add(new_order)
        db.flush()  # Flush to get order ID before inserting items

        # Process order items and calculate total price
        total_price = 0
        for item in order_data.order_items:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                total=item.total,
            )
            db.add(order_item)
            total_price += item.total            

            if isv >0:                
                fnl_amount=total_price + (total_price * isv)  
                isv_value=total_price * isv
            else:
                fnl_amount=total_price
                isv_value=0    
        # Update order's total price
        new_order.total_price = total_price
        new_order.updated_at = None
        new_order.final_price=fnl_amount  # Update final price with ISV
        new_order.isv=isv_value

        db.commit()
        db.refresh(new_order)

        return new_order, None

    except Exception as e:
        db.rollback()
        print(e)
        return None, "Error interno del servidor"





def update_order(db: Session, order_id: int, order_update: OrderUpdateSchema):
    # Retrieve the existing order
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None, "Order not found"

    try:
        # Update simple fields (if provided)
        if order_update.customer_name is not None:
            order.customer_name = order_update.customer_name
        if order_update.status is not None:
            order.status = order_update.status

        # Handle order items update
        if order_update.order_items is not None:
            existing_items = {item.product_id: item for item in order.order_items}
            incoming_product_ids = {item.product_id for item in order_update.order_items}

            # Remove products NOT in the incoming request
            for product_id in list(existing_items.keys()):
                if product_id not in incoming_product_ids:
                    db.delete(existing_items[product_id])  # Delete from DB

            new_items = []
            for item in order_update.order_items:
                if item.product_id in existing_items:
                    # Update existing order item
                    existing_item = existing_items[item.product_id]
                    existing_item.quantity = item.quantity
                    existing_item.total = item.total
                else:
                    # Add new order item
                    new_items.append(OrderItem(
                        order_id=order.id,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        total=item.total
                    ))

            # Add new items to the session
            db.add_all(new_items)

        # Update total price
        order.update_total_price()
        order.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(order)

        return order, None

    except Exception as e:
        db.rollback()
        print(e)
        return None, "Internal server error"
    
    

def get_order_report(db: Session, created_from: str = None, created_to: str = None, updated: str = None, month: str = None):
    try:
        today = datetime.utcnow().date()

        query = db.query(
            Order.status,
            func.count(Order.id).label("total_orders"),
            func.sum(Order.total_price).label("total_amount")
        ).group_by(Order.status)

        if month:
            query = query.filter(
                func.extract('year', Order.created_at) == int(month[:4]),
                func.extract('month', Order.created_at) == int(month[5:])
            )

        if created_from and created_to:
            query = query.filter(
                func.date(Order.created_at) >= created_from,
                func.date(Order.created_at) <= created_to
            )
        elif created_from:
            query = query.filter(func.date(Order.created_at) >= created_from)
        elif created_to:
            query = query.filter(func.date(Order.created_at) <= created_to)

        if updated:
            query = query.filter(func.date(Order.updated_at) == updated)

        if not (created_from or created_to or updated or month):
            query = query.filter(func.date(Order.created_at) == today)

        results = query.all()

        if not results:
            return None

        return {status: {"total_orders": total_orders, "total_amount": float(total_amount or 0)}
                for status, total_orders, total_amount in results}
    except Exception as e:
        print("Error in get_order_report:", e)
        return None


def get_product_report(db: Session, created: str = None, updated: str = None,month: str = None):
    # Get today's date
    today = datetime.utcnow().date()

    # Start query for product sales
    query = db.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_sales'),
        func.sum(OrderItem.total).label('total_amount')
    ).join(OrderItem).join(Order)  # Join with Order to access the date fields

    # Apply date filters based on created_at or updated_at in Order model
    if created:
        query = query.filter(func.date(Order.created_at) == created)
    elif updated:
        query = query.filter(func.date(Order.updated_at) == updated)
    elif month:
        print('Filtrando por mes')
        query = query.filter(
            func.extract('year', Order.created_at) == int(month[:4]),
            func.extract('month', Order.created_at) == int(month[5:]))
    else:
        query = query.filter(func.date(Order.created_at) == today)
        mes=extract('month', Order.created_at)
        print(mes)


    # Group by product to get the total sales and amount for each product
    query = query.group_by(Product.id)

    # Fetch the results
    results = query.all()

    # Serialize the results using the serializer
    serialized_report = serialize_product_report(results)

    return serialized_report