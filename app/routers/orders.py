from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.crud.orders import get_orders, get_order_by_id
from app.schemas.orders import OrderResponse
from app.schemas.response import ResponseModel
from app.models.orders import Order
from app.utils.utils import format_response, serialize_order,serialize_order_summary
from app.models.users import User
from app.auth.auth import get_current_user
from fastapi import Query
from sqlalchemy import cast, Date
from datetime import date
from sqlalchemy import func



router = APIRouter()

# ------------- OBTENER PEDIDOS (ORDERS) -----------------

@router.get("/orders", response_model=ResponseModel)
def get_orders_list(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    created: str = Query(None, description="Filter orders by creation date in YYYY-MM-DD format"),
    updated: str = Query(None, description="Filter orders by update date in YYYY-MM-DD format"),
    user_id: int = Query(None, description="Filter orders by user id")
):
    try:
        query = db.query(Order)

        if created:
            query = query.filter(func.date(Order.created_at) == created)  # Format to 'YYYY-MM-DD' and filter
        if updated:
            query = query.filter(func.date(Order.updated_at) == updated)  # Format to 'YYYY-MM-DD' and filter
        if user_id:
            query = query.filter(Order.user_id == user_id)

        orders = query.all()

        if not orders:
            return format_response(404, "No se encontraron pedidos")

        orders_serialized = [serialize_order_summary(order) for order in orders]

        return format_response(200, "Pedidos obtenidos con éxito", orders_serialized)

    except Exception as e:
        print(e)
        return format_response(500, "Error interno del servidor")



@router.get("/orders/{order_id}")
def get_order_details(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return format_response(404, "Orden no encontrada")

        order_serialized = serialize_order(order)
        return format_response(200, "Detalles de la orden obtenidos con éxito", order_serialized)

    except Exception as e:
        print(e)
        return format_response(500, "Error en el servidor")