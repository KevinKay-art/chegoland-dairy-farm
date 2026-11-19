"""Order routers: checkout, order API, HTML pages."""

from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.services.order_service import OrderService
from app.services.payment import PaymentService
from app.services.notification_service import NotificationService
from app.utils.security import get_current_user_optional, get_current_user, require_role
from app.config import settings
import uuid

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/api/v1/orders")
async def api_create_order(request: Request, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user_optional)):
    body = await request.json()
    cart = request.session.get("cart", {})
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    cart_items = [
        {"product_id": pid, "quantity": item["quantity"]}
        for pid, item in cart.items()
    ]

    subtotal = sum(item["price"] * item["quantity"] for item in cart.values())
    delivery_fee = 150.0

    order_service = OrderService(db)
    try:
        order = order_service.create_order_from_cart(
            user=current_user,
            cart_items=cart_items,
            customer_name=body.get("customer_name", ""),
            customer_phone=body.get("customer_phone", ""),
            customer_email=body.get("customer_email"),
            delivery_address=body.get("delivery_address", ""),
            delivery_date=body.get("delivery_date"),
            delivery_time_slot=body.get("delivery_time_slot"),
            payment_method=body.get("payment_method", "cash_on_delivery"),
            notes=body.get("notes"),
            subtotal=subtotal,
            delivery_fee=delivery_fee,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Clear cart
    request.session["cart"] = {}

    # If M-Pesa, initiate payment
    if body.get("payment_method") == "mpesa":
        phone = body.get("customer_phone", "")
        mpesa_result = await PaymentService().initiate_stk_push(phone, order.total_amount, order.order_number, "Dairy purchase")
        if mpesa_result.get("success"):
            order_service.record_payment(
                order_id=order.id, amount=order.total_amount,
                payment_method="mpesa", status="pending",
                checkout_request_id=mpesa_result.get("checkout_request_id"),
                phone_number=phone,
            )

    return {"success": True, "order_id": order.id, "order_number": order.order_number, "redirect": f"/order-confirmation/{order.id}"}


@router.get("/api/v1/orders")
async def api_list_orders(request: Request, db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user),
                          skip: int = 0, limit: int = 50):
    order_service = OrderService(db)
    if current_user.role == "admin":
        orders = order_service.list_orders(skip=skip, limit=limit)
    else:
        orders = order_service.list_orders(skip=skip, limit=limit, user_id=current_user.id)
    return [{"id": o.id, "order_number": o.order_number, "customer_name": o.customer_name,
             "total_amount": o.total_amount, "order_status": o.order_status,
             "payment_status": o.payment_status, "created_at": o.created_at} for o in orders]


@router.get("/api/v1/orders/{order_id}")
async def api_get_order(order_id: str, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    order_service = OrderService(db)
    order = order_service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role != "admin" and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"id": order.id, "order_number": order.order_number, "customer_name": order.customer_name,
            "total_amount": o.total_amount if False else order.total_amount,
            "order_status": order.order_status, "payment_status": order.payment_status,
            "payment_method": order.payment_method, "delivery_address": order.delivery_address,
            "delivery_date": order.delivery_date, "delivery_time_slot": order.delivery_time_slot,
            "items": [{"product_name": i.product_name, "quantity": i.quantity, "unit_price": i.unit_price, "total_price": i.total_price} for i in order.items]}


@router.put("/api/v1/orders/{order_id}/status")
async def api_update_order_status(order_id: str, order_status: str = Form(...),
                                  payment_status: str = Form(None),
                                  db: Session = Depends(get_db),
                                  current_user: User = Depends(require_role(["admin"]))):
    order_service = OrderService(db)
    order = order_service.update_order_status(order_id, order_status=order_status, payment_status=payment_status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"success": True, "message": "Order updated"}