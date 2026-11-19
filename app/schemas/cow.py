from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class CowBase(BaseModel):
    tag_number: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    breed: str = Field(..., min_length=1, max_length=50)
    date_of_birth: Optional[date] = None
    photo_url: Optional[str] = None
    status: Optional[str] = "lactating"
    daily_avg_yield: Optional[float] = 0.0
    notes: Optional[str] = None


class CowCreate(CowBase):
    pass


class CowOut(CowBase):
    id: str

    model_config = {"from_attributes": True}


class CowUpdate(BaseModel):
    tag_number: Optional[str] = None
    name: Optional[str] = None
    breed: Optional[str] = None
    date_of_birth: Optional[date] = None
    photo_url: Optional[str] = None
    status: Optional[str] = None
    daily_avg_yield: Optional[float] = None
    notes: Optional[str] = None