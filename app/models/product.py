from sqlalchemy import Column, String, Float, Integer, Boolean, Text, Index
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)  # milk, dairy, eggs, manure, etc.
    price = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # litre, 500ml, kg, piece
    stock_quantity = Column(Integer, default=0, nullable=False)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("ix_products_category", "category"),
        Index("ix_products_is_active", "is_active"),
        Index("ix_products_is_featured", "is_featured"),
    )