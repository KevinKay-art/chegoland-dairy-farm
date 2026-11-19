from sqlalchemy import Column, String, Float, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)  # mpesa, cash_on_delivery
    status = Column(String, default="pending", nullable=False)  # pending, completed, failed, refunded
    transaction_id = Column(String, nullable=True, index=True)
    mpesa_receipt_number = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    checkout_request_id = Column(String, nullable=True, index=True)
    merchant_request_id = Column(String, nullable=True)
    response_code = Column(String, nullable=True)
    response_description = Column(String, nullable=True)
    raw_callback = Column(Text, nullable=True)
    created_at = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)

    order = relationship("Order", back_populates="payments")

    __table_args__ = (
        Index("ix_payments_order_id", "order_id"),
        Index("ix_payments_status", "status"),
    )