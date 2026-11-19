"""Product routers: HTML + API for products."""

from fastapi import APIRouter, Request, Depends, Query, Form, HTTPException, status, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.utils.security import get_current_user_optional, require_role
from app.utils.image import save_uploaded_image
from app.config import settings
from pathlib import Path
import uuid

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = Path("app/static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/api/v1/products", response_model=list)
async def api_list_products(db: Session = Depends(get_db),
                            search: str = Query(None), category: str = Query(None),
                            skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    query = db.query(Product).filter(Product.is_active == True)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if category:
        query = query.filter(Product.category == category)
    products = query.offset(skip).limit(limit).all()
    return [
        {
            "id": p.id, "name": p.name, "slug": p.slug, "description": p.description,
            "category": p.category, "price": p.price, "unit": p.unit,
            "stock_quantity": p.stock_quantity, "image_url": p.image_url,
            "is_active": p.is_active, "is_featured": p.is_featured,
        }
        for p in products
    ]


@router.get("/api/v1/products/{product_id}", response_model=dict)
async def api_get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "id": product.id, "name": product.name, "slug": product.slug,
        "description": product.description, "category": product.category,
        "price": product.price, "unit": product.unit,
        "stock_quantity": product.stock_quantity, "image_url": product.image_url,
        "is_active": product.is_active, "is_featured": product.is_featured,
    }


@router.post("/api/v1/products", response_model=dict)
async def api_create_product(name: str = Form(...), slug: str = Form(...),
                             description: str = Form(""), category: str = Form(...),
                             price: float = Form(...), unit: str = Form("litre"),
                             stock_quantity: int = Form(0),
                             is_active: str = Form("true"),
                             is_featured: str = Form("false"),
                             image: UploadFile = File(None),
                             db: Session = Depends(get_db),
                             current_user: User = Depends(require_role(["admin"]))):
    image_url = None
    if image:
        image_url = save_uploaded_image(image, UPLOAD_DIR)

    product = Product(
        id=str(uuid.uuid4()), name=name, slug=slug, description=description,
        category=category, price=price, unit=unit, stock_quantity=stock_quantity,
        image_url=image_url, is_active=(is_active == "true"),
        is_featured=(is_featured == "true"),
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"id": product.id, "name": product.name, "slug": product.slug, "message": "Product created"}


@router.put("/api/v1/products/{product_id}", response_model=dict)
async def api_update_product(product_id: str, name: str = Form(None), slug: str = Form(None),
                             description: str = Form(None), category: str = Form(None),
                             price: float = Form(None), unit: str = Form(None),
                             stock_quantity: int = Form(None),
                             is_active: str = Form(None), is_featured: str = Form(None),
                             image: UploadFile = File(None),
                             db: Session = Depends(get_db),
                             current_user: User = Depends(require_role(["admin"]))):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if name is not None: product.name = name
    if slug is not None: product.slug = slug
    if description is not None: product.description = description
    if category is not None: product.category = category
    if price is not None: product.price = price
    if unit is not None: product.unit = unit
    if stock_quantity is not None: product.stock_quantity = stock_quantity
    if is_active is not None: product.is_active = (is_active == "true")
    if is_featured is not None: product.is_featured = (is_featured == "true")
    if image:
        product.image_url = save_uploaded_image(image, UPLOAD_DIR)
    db.commit()
    db.refresh(product)
    return {"id": product.id, "message": "Product updated"}


@router.delete("/api/v1/products/{product_id}", response_model=dict)
async def api_delete_product(product_id: str, db: Session = Depends(get_db),
                             current_user: User = Depends(require_role(["admin"]))):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}