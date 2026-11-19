from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SubscriptionBase(BaseModel):
    product_id: str
    quantity: int = Field(default=1, ge=1)
    frequency: str = Field(default="daily", pattern="^(daily|weekly)$")
    start_date: str
    end_date: Optional[str] = None
    is_active: Optional[bool] = True
    next_delivery_date: Optional[str] = None
    notes: Optional[str] = None


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionOut(SubscriptionBase):
    id: str
    user_id: str

    model_config = {"from_attributes": True}


class SubscriptionUpdate(BaseModel):
    quantity: Optional[int] = Field(default=None, ge=1)
    frequency: Optional[str] = Field(default=None, pattern="^(daily|weekly)$")
    end_date: Optional[str] = None
    is_active: Optional[bool] = None
    next_delivery_date: Optional[str] = None
    notes: Optional[str] = None