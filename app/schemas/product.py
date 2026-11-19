from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)
    stock_quantity: int = Field(default=0, ge=0)
    image_url: Optional[str] = None
    is_active: Optional[bool] = True
    is_featured: Optional[bool] = False


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: str

    model_config = {"from_attributes": True}


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    unit: Optional[str] = None
    stock_quantity: Optional[int] = Field(default=None, ge=0)
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None