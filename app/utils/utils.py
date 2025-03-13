from fastapi.responses import JSONResponse
import uuid
from app.models.product import Product
from app.models.orders import Order, OrderItem
from sqlalchemy.orm import class_mapper
from typing import List


def format_response(http_code: int, message: str, data=None,request=None):
    """Formats API responses dynamically based on HTTP status codes."""
    status_map = {
        201: "Ok",
        200: "Ok",        
        400: "bad_request",
        404: "No hay informacion",
        500: "error",
    }

    status = status_map.get(http_code, "error")  # Default to 'error' if unknown code
    uti = str(uuid.uuid4())

    return JSONResponse(
        status_code=http_code,
        content={
            "uti": uti,                        
            "message": message,
            "status": status,
            "http_code": http_code,
            "data": data or []        },
    )


def serialize_product(products):
    if isinstance(products, list):
        return [
            {
                **{column.name: getattr(product, column.name) for column in class_mapper(Product).columns},
                "category_name": product.category.name if product.category else None  # ✅ Add category name
            }
            for product in products
        ]
    else:
        return {
            **{column.name: getattr(products, column.name) for column in class_mapper(Product).columns},
            "category_name": products.category.name if products.category else None  # ✅ Add category name
        }

    
    
def serialize_category(categories):
    if isinstance(categories, list):
        return [{"id": cat.id, "name": cat.name} for cat in categories]
    return {
        "id": categories.id,
        "name": categories.name
    }



def serialize_order(order):
    if isinstance(order, list):
        return [serialize_order(o) for o in order]

    return {
        "id": order.id,
        "user_id": order.user_id,
        "customer_name": order.customer_name,
        "total_price": order.total_price,
        "status": order.status,
        "created_at": order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else None,
        "updated_at": order.updated_at.strftime('%Y-%m-%d %H:%M:%S') if order.updated_at else None,
        "order_items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "total": item.total
            } for item in order.order_items
        ]
    }




def serialize_order_summary(order):
    return {
        "id": order.id,
        "user_id": order.user_id,
        "customer_name": order.customer_name,
        "total_price": order.total_price,
        "status": order.status,
        "created_at": order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else None,
        "updated_at": order.updated_at.strftime('%Y-%m-%d %H:%M:%S') if order.updated_at else None
    }



def serialize_product_report(products_data: List):
    """
    Serializes the product sales report data into a suitable structure.
    """

    # Map the results to a list of dictionaries
    return [
        {
            "product_name": product_name,
            "total_sales": total_sales or 0,
            "total_amount": float(total_amount or 0)
        }
        for product_name, total_sales, total_amount in products_data
    ]