"""Order service: cart-to-order conversion, atomic stock reduction, status flow."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.payment import Payment
from app.models.user import User
import uuid


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def create_order_from_cart(self, user: Optional[User], cart_items: List[Dict[str, Any]],
                               customer_name: str, customer_phone: str,
                               customer_email: Optional[str], delivery_address: str,
                               delivery_date: Optional[str], delivery_time_slot: Optional[str],
                               payment_method: str, notes: Optional[str] = None,
                               subtotal: float = 0.0, delivery_fee: float = 0.0) -> Order:
        total_amount = subtotal + delivery_fee
        order = Order(
            id=str(uuid.uuid4()),
            order_number=f"CG{datetime.now(timezone.utc).strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}",
            user_id=user.id if user else None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            delivery_address=delivery_address,
            delivery_date=delivery_date,
            delivery_time_slot=delivery_time_slot,
            payment_method=payment_method,
            payment_status="pending",
            order_status="pending",
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total_amount=total_amount,
            notes=notes,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        self.db.add(order)
        self.db.flush()

        for item in cart_items:
            product = self.db.query(Product).filter(Product.id == item["product_id"]).with_for_update().first()
            if not product:
                raise ValueError(f"Product {item['product_id']} not found")
            if product.stock_quantity < item["quantity"]:
                raise ValueError(f"Insufficient stock for {product.name}. Available: {product.stock_quantity}")

            product.stock_quantity -= item["quantity"]
            order_item = OrderItem(
                id=str(uuid.uuid4()),
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                quantity=item["quantity"],
                unit_price=product.price,
                total_price=product.price * item["quantity"],
            )
            self.db.add(order_item)

        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id).first()

    def get_order_by_number(self, order_number: str) -> Optional[Order]:
        return self.db.query(Order).filter(Order.order_number == order_number).first()

    def list_orders(self, skip: int = 0, limit: int = 50, user_id: Optional[str] = None,
                    status: Optional[str] = None) -> List[Order]:
        query = self.db.query(Order)
        if user_id:
            query = query.filter(Order.user_id == user_id)
        if status:
            query = query.filter(Order.order_status == status)
        return query.offset(skip).limit(limit).all()

    def count_orders(self, user_id: Optional[str] = None, status: Optional[str] = None) -> int:
        query = self.db.query(Order)
        if user_id:
            query = query.filter(Order.user_id == user_id)
        if status:
            query = query.filter(Order.order_status == status)
        return query.count()

    def update_order_status(self, order_id: str, order_status: Optional[str] = None,
                            payment_status: Optional[str] = None) -> Optional[Order]:
        order = self.get_order_by_id(order_id)
        if not order:
            return None
        if order_status is not None:
            order.order_status = order_status
        if payment_status is not None:
            order.payment_status = payment_status
        order.updated_at = datetime.now(timezone.utc).isoformat()
        self.db.commit()
        self.db.refresh(order)
        return order

    def record_payment(self, order_id: str, amount: float, payment_method: str,
                       status: str = "completed", transaction_id: Optional[str] = None,
                       mpesa_receipt_number: Optional[str] = None,
                       phone_number: Optional[str] = None,
                       checkout_request_id: Optional[str] = None,
                       raw_callback: Optional[str] = None) -> Payment:
        payment = Payment(
            id=str(uuid.uuid4()),
            order_id=order_id,
            amount=amount,
            payment_method=payment_method,
            status=status,
            transaction_id=transaction_id or f"txn_{uuid.uuid4().hex[:12]}",
            mpesa_receipt_number=mpesa_receipt_number,
            phone_number=phone_number,
            checkout_request_id=checkout_request_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_today_sales(self) -> float:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        orders = self.db.query(Order).filter(
            Order.created_at.like(f"{today}%"),
            Order.payment_status == "paid",
        ).all()
        return sum(o.total_amount for o in orders)

    def get_monthly_revenue(self, year: int, month: int) -> float:
        prefix = f"{year}-{month:02d}"
        orders = self.db.query(Order).filter(
            Order.created_at.like(f"{prefix}%"),
            Order.payment_status == "paid",
        ).all()
        return sum(o.total_amount for o in orders)

    def get_pending_orders_count(self) -> int:
        return self.db.query(Order).filter(Order.order_status == "pending").count()