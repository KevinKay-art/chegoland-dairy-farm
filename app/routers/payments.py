"""Payment routers: M-Pesa STK Push, callback, payment status."""

from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.order import Order
from app.models.payment import Payment
from app.services.payment import PaymentService
from app.services.order_service import OrderService
from app.services.notification_service import NotificationService
from app.utils.security import get_current_user, require_role
from app.config import settings
import json

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/api/v1/payments/mpesa/stk-push")
async def api_mpesa_stk_push(request: Request, db: Session = Depends(get_db),
                             current_user = Depends(get_current_user)):
    body = await request.json()
    phone = body.get("phone_number", "")
    amount = float(body.get("amount", 0))
    order_id = body.get("order_id", "")

    if not phone or not amount:
        raise HTTPException(status_code=400, detail="Phone number and amount required")

    result = await PaymentService().initiate_stk_push(phone, amount, f"ORDER-{order_id}", "Dairy purchase")
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "M-Pesa error"))

    # Store pending payment reference
    if order_id:
        order_service = OrderService(db)
        order_service.record_payment(
            order_id=order_id, amount=amount, payment_method="mpesa",
            status="pending", checkout_request_id=result.get("checkout_request_id"),
            phone_number=phone,
        )

    return {"success": True, "checkout_request_id": result.get("checkout_request_id"),
            "message": result.get("customer_message", "STK push initiated"),
            "mock_mode": result.get("mock_mode", False)}


@router.post("/api/v1/payments/mpesa/callback")
async def mpesa_callback(request: Request, db: Session = Depends(get_db)):
    """M-Pesa Daraja callback endpoint."""
    payload = await request.json()
    stk_callback = payload.get("Body", {}).get("stkCallback", {})
    checkout_request_id = stk_callback.get("CheckoutRequestID")
    result_code = stk_callback.get("ResultCode")
    result_desc = stk_callback.get("ResultDesc", "")

    # Find payment by checkout_request_id
    payment = db.query(Payment).filter(Payment.checkout_request_id == checkout_request_id).first()
    if not payment:
        return JSONResponse({"status": "error", "message": "Payment not found"}, status_code=404)

    order = db.query(Order).filter(Order.id == payment.order_id).first()
    success = result_code == "0"

    if success:
        metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
        receipt = None
        amount = None
        phone = None
        for item in metadata:
            if item.get("Name") == "MpesaReceiptNumber":
                receipt = item.get("Value")
            elif item.get("Name") == "Amount":
                amount = item.get("Value")
            elif item.get("Name") == "PhoneNumber":
                phone = item.get("Value")

        payment.status = "completed"
        payment.mpesa_receipt_number = receipt
        payment.phone_number = str(phone) if phone else None
        payment.transaction_id = receipt or f"txn_{payment.id[:8]}"
        order.payment_status = "paid"
        order.order_status = "processing"
        db.commit()

        # Send notification
        NotificationService().send_order_status_update(
            order.customer_phone or "", order.order_number, "Paid - Processing"
        )
    else:
        payment.status = "failed"
        order.payment_status = "failed"
        order.order_status = "cancelled"
        db.commit()

    return JSONResponse({"status": "success", "message": "Callback processed"})


@router.post("/api/v1/payments/mpesa/simulate-callback")
async def simulate_mpesa_callback(request: Request):
    """Simulate M-Pesa callback (mock mode only)."""
    body = await request.json()
    checkout_request_id = body.get("checkout_request_id")
    success = body.get("success", True)
    result = await PaymentService().simulate_callback(
        checkout_request_id, success,
        body.get("receipt_number"), body.get("phone_number"), body.get("amount")
    )
    return {"success": True, "simulated": result}


@router.get("/api/v1/payments/{order_id}", response_model=dict)
async def api_get_payment(order_id: str, db: Session = Depends(get_db),
                          current_user = Depends(get_current_user)):
    payment = db.query(Payment).filter(Payment.order_id == order_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {
        "id": payment.id, "amount": payment.amount, "payment_method": payment.payment_method,
        "status": payment.status, "mpesa_receipt_number": payment.mpesa_receipt_number,
        "transaction_id": payment.transaction_id, "created_at": payment.created_at,
    }