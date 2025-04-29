from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.crud.orders import create_order,update_order,get_order_report,get_product_report
from app.schemas.orders import OrderResponse,OrderUpdateSchema,OrderCreateSchema,ProductReport
from app.schemas.response import ResponseModel
from app.models.orders import Order,OrderItem
from app.utils.utils import format_response, serialize_order,serialize_order_summary,generate_order_receipt,send_to_printer
from app.models.users import User
from app.auth.auth import get_current_user
from fastapi import Query
from sqlalchemy import func
from datetime import datetime,timedelta
import json
from fastapi.responses import PlainTextResponse
from sqlalchemy import case, distinct



router = APIRouter()

# ------------- OBTENER PEDIDOS (ORDERS) -----------------

@router.get("/orders", response_model=ResponseModel)
def get_orders_list(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    created: str = Query(None, description="Filter orders by creation date in YYYY-MM-DD format"),
    updated: str = Query(None, description="Filter orders by update date in YYYY-MM-DD format"),
    username: str = Query(None, description="Filter orders by user id")
):
    try:
        
        today_date = datetime.today().strftime('%Y-%m-%d')        
        
        query = db.query(Order)
        orders=query.filter(Order.created_at >= today_date).order_by(Order.id.desc()).all()


        if created:
            query = query.filter(func.date(Order.created_at) == created)  # Filter by created date
            orders = query.order_by(Order.id.desc()).all()            
        if updated:
            query = query.filter(func.date(Order.updated_at) == updated)  # Filter by updated date
            orders = query.order_by(Order.id.desc()).all()            
        if username:
            query = query.filter(Order.username == username)
            orders = query.order_by(Order.id.desc()).all()


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



@router.get("/orderDetails/{order_id}")
def get_order_details(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
              
        
        if not order:
            return format_response(404, "Orden no encontrada")

        order_serialized = serialize_order(order)
#        receipt_text = generate_order_receipt(order_serialized)
#        print(receipt_text)        
        
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

    respuesta=format_response(201, "Pedido creado con éxito", serialize_order(new_order))

    respuesta_dict = json.loads(respuesta.body)
    order_id = respuesta_dict["data"]["id"]

    print('Respuesta ID:',order_id)


    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    
    order_serialized = serialize_order(order)
    receipt_text = generate_order_receipt(order_serialized)    
    send_to_printer(receipt_text)

    return respuesta

    
    
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
    created_from: str = Query(None, description="Filter by creation start date (YYYY-MM-DD)"),
    created_to: str = Query(None, description="Filter by creation end date (YYYY-MM-DD)"),
    updated: str = Query(None, description="Filter by update date (YYYY-MM-DD)"),    
    month: str = Query(None),        
    db: Session = Depends(get_db)
):
    report = get_order_report(db, created_from, created_to, updated, month)

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
    
    
    
    
    


@router.delete("/orders/{order_id}", response_model=ResponseModel)
def delete_order_route(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            return format_response(404, "Orden no encontrada")

        db.delete(order)
        db.commit()

        return format_response(200, "Orden eliminada exitosamente")

    except Exception as e:
        print(e)
        return format_response(500, "Error interno del servidor")




@router.get("/orderDailyReport")
def get_daily_order_report(
    db: Session = Depends(get_db),
    created_from: str = Query(None, description="Start date in YYYY-MM-DD format"),
    created_to: str = Query(None, description="End date in YYYY-MM-DD format")
):
    try:
        today = datetime.today()
        default_start = (today - timedelta(days=7)).strftime('%Y-%m-%d')  # Default to last 7 days
        default_end = today.strftime('%Y-%m-%d')
        
        # Use date range provided by the user or default to the last 7 days
        from_date = created_from if created_from else default_start
        to_date = created_to if created_to else default_end
        
        # Subquery to calculate the total amount excluding products with ID 15 (ENTRADAS)
        # for each order and day
        subquery = db.query(
            func.date(Order.created_at).label('date'),
            Order.id.label('order_id'),
            func.sum(
                case(
                    (OrderItem.product_id != 15, OrderItem.total),
                    else_=0
                )
            ).label('adjusted_total')
        ).join(
            OrderItem, Order.id == OrderItem.order_id
        ).filter(
            func.date(Order.created_at) >= from_date,
            func.date(Order.created_at) <= to_date,
            Order.status == "enviada"
        ).group_by(
            func.date(Order.created_at),
            Order.id
        ).subquery()
        
        # Main query to aggregate the results by day
        query = db.query(
            subquery.c.date,
            func.sum(subquery.c.adjusted_total).label('total_amount'),
            func.count(distinct(subquery.c.order_id)).label('total_orders')
        ).group_by(
            subquery.c.date
        ).order_by(
            subquery.c.date.asc()
        )
        
        # Execute the query
        results = query.all()
        
        # If no data found, return an error response
        if not results:
            return format_response(404, "No se encontraron reportes de ordenes")
        
        # Prepare the response data
        daily_reports = []
        for row in results:
            daily_reports.append({
                "date": row.date,
                "total_amount": float(row.total_amount) if row.total_amount else 0,
                "total_orders": row.total_orders
            })
        
        # Return the formatted response
        return format_response(200, "Reporte diario generado exitosamente", daily_reports)
    
    except Exception as e:
        print(e)
        return format_response(500, f"Error interno del servidor: {str(e)}")




@router.get("/entradasDailyReport")
def get_entradas_daily_report(
    db: Session = Depends(get_db),
    created_from: str = Query(None, description="Start date in YYYY-MM-DD format"),
    created_to: str = Query(None, description="End date in YYYY-MM-DD format")
):
    try:
        today = datetime.today()
        default_start = (today - timedelta(days=7)).strftime('%Y-%m-%d')  # Default to last 7 days
        default_end = today.strftime('%Y-%m-%d')
        
        # Use date range provided by the user or default to the last 7 days
        from_date = created_from if created_from else default_start
        to_date = created_to if created_to else default_end
        
        # Query to calculate the total amount of products with ID 15 (ENTRADAS) by day
        query = db.query(
            func.date(Order.created_at).label('date'),
            func.sum(OrderItem.total).label('entradas_total')
        ).join(
            OrderItem, Order.id == OrderItem.order_id
        ).filter(
            func.date(Order.created_at) >= from_date,
            func.date(Order.created_at) <= to_date,
            Order.status == "enviada",
            OrderItem.product_id == 15  # Only ENTRADAS products
        ).group_by(
            func.date(Order.created_at)
        ).order_by(
            func.date(Order.created_at).asc()
        )
        
        # Execute the query
        results = query.all()
        
        # If no data found, return an error response
        if not results:
            return format_response(404, "No se encontraron reportes de entradas")
        
        # Prepare the response data
        daily_reports = []
        for row in results:
            daily_reports.append({
                "date": row.date,
                "total_amount": float(row.entradas_total) if row.entradas_total else 0
            })
        
        # Return the formatted response
        return format_response(200, "Reporte diario de entradas generado exitosamente", daily_reports)
    
    except Exception as e:
        print(e)
        return format_response(500, f"Error interno del servidor: {str(e)}")




#---------------RECEIPT------------------


#@router.get("/orderReceipt/{order_id}")
#def get_order_receipt(order_id: int, db: Session = Depends(get_db)):
#    order = db.query(Order).filter(Order.id == order_id).first()
#    if not order:
#        raise HTTPException(status_code=404, detail="Orden no encontrada")

    
#    order_serialized = serialize_order(order)
#    receipt_text = generate_order_receipt(order_serialized)
    
    
 #   send_to_printer(receipt_text)

 #   return {
 #       "message": "Recibo enviado a impresión",
 #       "order_id": order.id
 #   }

