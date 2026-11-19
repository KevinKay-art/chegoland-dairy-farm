from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class HealthRecordBase(BaseModel):
    cow_id: str
    record_type: str = Field(..., pattern="^(health|vaccination)$")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    date: date
    next_due_date: Optional[date] = None
    cost: Optional[str] = None
    vet_name: Optional[str] = None
    notes: Optional[str] = None


class HealthRecordCreate(HealthRecordBase):
    pass


class HealthRecordOut(HealthRecordBase):
    id: str

    model_config = {"from_attributes": True}


class HealthRecordUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[date] = None
    next_due_date: Optional[date] = None
    cost: Optional[str] = None
    vet_name: Optional[str] = None
    notes: Optional[str] = None