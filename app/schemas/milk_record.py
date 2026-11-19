from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class MilkRecordBase(BaseModel):
    cow_id: str
    date: date
    session: str = Field(..., pattern="^(morning|evening)$")
    yield_litres: float = Field(..., ge=0)
    used_by_calves: Optional[float] = 0.0
    spoiled: Optional[float] = 0.0
    available_for_sale: Optional[float] = 0.0
    notes: Optional[str] = None


class MilkRecordCreate(MilkRecordBase):
    pass


class MilkRecordOut(MilkRecordBase):
    id: str

    model_config = {"from_attributes": True}


class MilkRecordUpdate(BaseModel):
    yield_litres: Optional[float] = Field(default=None, ge=0)
    used_by_calves: Optional[float] = None
    spoiled: Optional[float] = None
    available_for_sale: Optional[float] = None
    notes: Optional[str] = None