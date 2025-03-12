from fastapi.responses import JSONResponse
import uuid
from app.models.product import Product
from sqlalchemy.orm import class_mapper


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
        return [{column.name: getattr(product, column.name) for column in class_mapper(Product).columns} for product in products]
    else:
        return {column.name: getattr(products, column.name) for column in class_mapper(Product).columns}