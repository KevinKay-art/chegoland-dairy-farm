from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PaymentBase(BaseModel):
    order_id: str
    amount: float = Field(..., gt=0)
    payment_method: str
    status: Optional[str] = "pending"


class PaymentOut(PaymentBase):
    id: str
    transaction_id: Optional[str] = None
    mpesa_receipt_number: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PaymentCallback(BaseModel):
    checkout_request_id: str
    result_code: str
    result_desc: str
    mpesa_receipt_number: Optional[str] = None
    transaction_date: Optional[str] = None
    phone_number: Optional[str] = None
    amount: Optional[float] = None