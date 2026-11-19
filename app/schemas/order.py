from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OrderItemBase(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)


class OrderItemOut(OrderItemBase):
    id: str
    product_name: str
    unit_price: float
    total_price: float

    model_config = {"from_attributes": True}


class OrderBase(BaseModel):
    customer_name: str = Field(..., min_length=1)
    customer_phone: str = Field(..., min_length=1)
    customer_email: Optional[str] = None
    delivery_address: str = Field(..., min_length=1)
    delivery_date: Optional[str] = None
    delivery_time_slot: Optional[str] = None
    payment_method: str = Field(..., pattern="^(mpesa|cash_on_delivery)$")
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemBase] = Field(..., min_length=1)


class OrderOut(OrderBase):
    id: str
    order_number: str
    user_id: Optional[str] = None
    payment_status: str
    order_status: str
    subtotal: float
    delivery_fee: float
    total_amount: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[OrderItemOut] = []

    model_config = {"from_attributes": True}


class OrderUpdate(BaseModel):
    order_status: Optional[str] = None
    payment_status: Optional[str] = None
    delivery_date: Optional[str] = None
    delivery_time_slot: Optional[str] = None
    notes: Optional[str] = None