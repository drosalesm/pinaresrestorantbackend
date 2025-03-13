from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.crud.orders import create_order,update_order,get_order_report,get_product_report
from app.schemas.orders import OrderResponse,OrderUpdateSchema,OrderCreateSchema,ProductReport
from app.schemas.response import ResponseModel
from app.models.orders import Order,OrderItem
from app.utils.utils import format_response, serialize_order,serialize_order_summary
from app.models.users import User
from app.auth.auth import get_current_user
from fastapi import Query
from sqlalchemy import func
from datetime import datetime



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
            query = query.filter(func.date(Order.created_at) == created)  # Filter by created date
        if updated:
            query = query.filter(func.date(Order.updated_at) == updated)  # Filter by updated date
        if user_id:
            query = query.filter(Order.user_id == user_id)

        orders = query.all()

        if not orders:
            return format_response(404, "No se encontraron pedidos")

        # Organize orders dynamically by status
        grouped_orders = {}
        for order in orders:
            status = order.status if order.status else "unknown"
            if status not in grouped_orders:
                grouped_orders[status] = []
            grouped_orders[status].append(serialize_order_summary(order))

        return format_response(200, "Pedidos organizados por estado", grouped_orders)

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
    
    
    
    

@router.post("/orders", response_model=ResponseModel)
def create_order_endpoint(
    order_data: OrderCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_order, error = create_order(db, order_data)
    
    if error:
        return format_response(404 if "Usuario" in error else 500, error)

    return format_response(201, "Pedido creado con éxito", serialize_order(new_order))
    
    
    

    
    
@router.put("/orders/{order_id}")
def update_order_endpoint(
    order_id: int,
    order_update: OrderUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_order, error = update_order(db, order_id, order_update)

    if error:
        return format_response(404 if "not found" in error else 500, error)

    return format_response(200, "Order updated successfully", serialize_order_summary(updated_order))


#---------------REPORTES

@router.get("/reports/orders")
def get_order_report_router(
    created: str = Query(None, description="Filter by creation date (YYYY-MM-DD)"),
    updated: str = Query(None, description="Filter by update date (YYYY-MM-DD)"),
    month: str = Query(None),        
    db: Session = Depends(get_db)
):
    report = get_order_report(db, created, updated,month)

    if report is None:
        return format_response(404, "No hay informacion para el dia seleccionado")

    return format_response(200, "Reporte generado exitosamente", report)



@router.get("/reports/products")
def get_product_report_view(
    created: str = Query(None),
    updated: str = Query(None),
    month: str = Query(None),    
    db: Session = Depends(get_db)
):
    try:
        report = get_product_report(db, created, updated,month)

        # If no data is found, return a proper message
        if not report:
            return format_response(404, "No data found for the selected filters", [])

        return format_response(200, "Product report generated successfully", report)

    except Exception as e:
        print(e)
        return format_response(500, "Internal server error")