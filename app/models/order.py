from sqlalchemy import Column, String, Float, Integer, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    customer_email = Column(String, nullable=True)
    delivery_address = Column(String, nullable=False)
    delivery_date = Column(String, nullable=True)
    delivery_time_slot = Column(String, nullable=True)
    payment_method = Column(String, nullable=False)  # mpesa, cash_on_delivery
    payment_status = Column(String, default="pending", nullable=False)  # pending, paid, failed, refunded
    order_status = Column(String, default="pending", nullable=False)  # pending, paid, processing, out_for_delivery, delivered, cancelled
    subtotal = Column(Float, default=0.0, nullable=False)
    delivery_fee = Column(Float, default=0.0, nullable=False)
    total_amount = Column(Float, default=0.0, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_orders_user_id", "user_id"),
        Index("ix_orders_order_status", "order_status"),
        Index("ix_orders_payment_status", "payment_status"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")

    __table_args__ = (Index("ix_order_items_order_id", "order_id"), Index("ix_order_items_product_id", "product_id"))