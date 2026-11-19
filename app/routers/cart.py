"""Cart routers: session-based cart API."""

from fastapi import APIRouter, Request, Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Product
from app.utils.security import get_current_user_optional

router = APIRouter()


def get_cart(request: Request) -> dict:
    return request.session.setdefault("cart", {})


@router.get("/api/v1/cart")
async def api_get_cart(request: Request):
    cart = get_cart(request)
    # Enrich with product details
    return {"items": cart, "count": sum(v.get("quantity", 0) for v in cart.values())}


@router.post("/api/v1/cart/add")
async def api_add_to_cart(request: Request, product_id: str = Body(...), quantity: int = Body(1),
                          db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock_quantity < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    cart = get_cart(request)
    if product_id in cart:
        cart[product_id]["quantity"] += quantity
    else:
        cart[product_id] = {
            "product_id": product_id,
            "name": product.name,
            "price": product.price,
            "unit": product.unit,
            "quantity": quantity,
            "image_url": product.image_url,
        }
    request.session["cart"] = cart
    return {"success": True, "message": "Added to cart", "count": sum(v.get("quantity", 0) for v in cart.values())}


@router.post("/api/v1/cart/update")
async def api_update_cart(request: Request, product_id: str = Body(...), quantity: int = Body(...)):
    cart = get_cart(request)
    if product_id not in cart:
        raise HTTPException(status_code=404, detail="Item not in cart")
    if quantity <= 0:
        del cart[product_id]
    else:
        cart[product_id]["quantity"] = quantity
    request.session["cart"] = cart
    return {"success": True, "count": sum(v.get("quantity", 0) for v in cart.values())}


@router.post("/api/v1/cart/remove")
async def api_remove_from_cart(request: Request, payload: dict = Body(...)):
    product_id = payload.get("product_id")
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")
    cart = get_cart(request)
    cart.pop(product_id, None)
    request.session["cart"] = cart
    return {"success": True, "count": sum(v.get("quantity", 0) for v in cart.values())}


@router.post("/api/v1/cart/clear")
async def api_clear_cart(request: Request):
    request.session["cart"] = {}
    return {"success": True}