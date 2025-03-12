from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.crud.product import get_product_by_id, get_all_products
from app.schemas.product import ProductResponse,ProductCreate,ProductUpdate
from app.schemas.response import ResponseModel
from app.models.product import Product
from app.models.categoryProducts import CategoryProducts
from fastapi.responses import JSONResponse
from app.crud.log import create_log_entry
from app.utils.utils import format_response,serialize_product
from sqlalchemy.orm import class_mapper
from app.models.users import User  
from app.auth.auth import get_current_user
router = APIRouter()
from collections import defaultdict

#-------------OBTENER PRODUCTOS

#@router.get("/products", response_model=ProductResponse)
#def get_products(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
        
#    try:
#        products = db.query(Product).all()

#        if not products:
#            return format_response(404, "No se encontró información de productos")

        # Serialize the list of products
#        products_serialized = serialize_product(products)

#        return format_response(200, "Se obtuvieron los productos de forma exitosa", products_serialized)

#    except Exception as e:
#        print(e)
#        return format_response(500, "Internal Server Error")


@router.get("/products", response_model=ResponseModel)
def get_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        products = db.query(Product).all()

        if not products:
            return format_response(404, "No se encontró información de productos")

        categorized_products = defaultdict(list)
        uncategorized = []

        for product in products:
            product_data = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "inventory": product.inventory,
                "id_category": product.category_id,
                "name_category": product.category.name if product.category else None
            }

            if product.category and product.category.name:
                categorized_products[product.category.name].append(product_data)
            else:
                uncategorized.append(product_data)

        response_data = {"categories": dict(categorized_products), "sinDefinir": uncategorized}

        return format_response(200, "Productos organizados por categoría", response_data)

    except Exception as e:
        print(e)
        return format_response(500, "Internal Server Error")


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return format_response(404, "Producto no encontrado")

    product_serialized = serialize_product(product)
    return format_response(200, "Producto obtenido con éxito", product_serialized)



#-----------------------CREAR PRODUCTOS

@router.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    try:

        if product.category_id:
            category = db.query(CategoryProducts).filter(CategoryProducts.id == product.category_id).first()
            if not category:
                return format_response(400, "La categoría especificada no existe")


        new_product = Product(
            name=product.name,
            description=product.description,
            price=product.price,
            category_id=product.category_id  # Set category_id if provided
            
        )

        # Add to database
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        # Serialize the product
        product_dict = serialize_product(new_product)

        # Return the serialized product as a response
        return format_response(201, "Se creo el producto de forma exitosa", product_dict)
    
    except Exception as e:
        print(e)
        return format_response(500, "Error de procesamiento")


#---------------ACTUALIZAR PRODUCTOS

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return format_response(404, "Producto no encontrado")


    if product_data.category_id:
        category = db.query(CategoryProducts).filter(CategoryProducts.id == product_data.category_id).first()
        if not category:
            return format_response(400, "La categoría especificada no existe")


    # Update only provided fields
    if product_data.name:
        product.name = product_data.name
    if product_data.description:
        product.description = product_data.description
    if product_data.price:
        product.price = product_data.price
    if product_data.category_id is not None:
        product.category_id = product_data.category_id  # Update category_id if provided


    db.commit()
    db.refresh(product)

    product_serialized = serialize_product(product)
    return format_response(200, "Producto actualizado con éxito", product_serialized)

#-----------ELIMINAR PRODUCTOS


@router.delete("/products/{product_id}", response_model=ProductResponse)
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return format_response(404, "Producto no encontrado")

    db.delete(product)
    db.commit()

    return format_response(200, "Producto eliminado con éxito")