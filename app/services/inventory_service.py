"""Inventory service: product stock management, low-stock alerts."""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.product import Product


class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_low_stock(self, threshold: int = 5) -> List[Product]:
        return self.db.query(Product).filter(Product.stock_quantity <= threshold, Product.is_active == True).all()

    def adjust_stock(self, product_id: str, delta: int) -> Optional[Product]:
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        product.stock_quantity = max(0, product.stock_quantity + delta)
        self.db.commit()
        self.db.refresh(product)
        return product