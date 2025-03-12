from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.categoryProducts import CategoryProducts
from app.schemas.categoryProducts import CategoryProductCreate, CategoryProductUpdate, CategoryProductResponse
from app.schemas.response import ResponseModel
from app.utils.utils import format_response, serialize_category
from app.models.users import User
from app.auth.auth import get_current_user

router = APIRouter()

#------------- OBTENER CATEGORÍAS DE PRODUCTOS -------------
@router.get("/categories", response_model=CategoryProductResponse)
def get_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        categories = db.query(CategoryProducts).all()
        if not categories:
            return format_response(404, "No se encontraron categorías de productos")

        categories_serialized = serialize_category(categories)
        return format_response(200, "Categorías obtenidas con éxito", categories_serialized)
    except Exception as e:
        print(e)
        return format_response(500, "Error interno del servidor")

#------------- OBTENER UNA CATEGORÍA POR ID -------------
@router.get("/categories/{category_id}", response_model=CategoryProductResponse)
def get_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = db.query(CategoryProducts).filter(CategoryProducts.id == category_id).first()
    if not category:
        return format_response(404, "Categoría no encontrada")

    category_serialized = serialize_category(category)
    return format_response(200, "Categoría obtenida con éxito", category_serialized)

#------------- CREAR UNA NUEVA CATEGORÍA -------------
@router.post("/categories", response_model=CategoryProductResponse)
def create_category(category: CategoryProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        new_category = CategoryProducts(name=category.name)  # Only 'name' is passed here
        db.add(new_category)
        db.commit()
        db.refresh(new_category)

        category_serialized = serialize_category(new_category)
        return format_response(201, "Categoría creada exitosamente", category_serialized)
    except Exception as e:
        print(e)
        return format_response(500, "Error al procesar la solicitud")

#------------- ACTUALIZAR UNA CATEGORÍA -------------
@router.put("/categories/{category_id}", response_model=CategoryProductResponse)
def update_category(category_id: int, category_data: CategoryProductUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = db.query(CategoryProducts).filter(CategoryProducts.id == category_id).first()
    if not category:
        return format_response(404, "Categoría no encontrada")

    if category_data.name:
        category.name = category_data.name
    
    db.commit()
    db.refresh(category)

    category_serialized = serialize_category(category)
    return format_response(200, "Categoría actualizada con éxito", category_serialized)

#------------- ELIMINAR UNA CATEGORÍA -------------
@router.delete("/categories/{category_id}", response_model=CategoryProductResponse)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = db.query(CategoryProducts).filter(CategoryProducts.id == category_id).first()
    if not category:
        return format_response(404, "Categoría no encontrada")

    db.delete(category)
    db.commit()

    return format_response(200, "Categoría eliminada con éxito")
