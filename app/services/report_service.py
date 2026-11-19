"""Report service: sales and production analytics, CSV export."""

import csv
import io
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.order import Order
from app.models.milk_record import MilkRecord
from app.models.product import Product
from app.models.user import User


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def sales_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        orders = self.db.query(Order).filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.payment_status == "paid",
        ).all()
        return [
            {
                "order_number": o.order_number,
                "customer_name": o.customer_name,
                "created_at": o.created_at,
                "total_amount": o.total_amount,
                "payment_method": o.payment_method,
                "order_status": o.order_status,
            }
            for o in orders
        ]

    def production_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        records = self.db.query(MilkRecord).filter(
            MilkRecord.date >= start_date,
            MilkRecord.date <= end_date,
        ).all()
        return [
            {
                "cow_id": r.cow_id,
                "date": r.date.isoformat() if hasattr(r.date, "isoformat") else str(r.date),
                "session": r.session,
                "yield_litres": r.yield_litres,
                "available_for_sale": r.available_for_sale,
            }
            for r in records
        ]

    def top_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        from app.models.order import OrderItem
        results = (
            self.db.query(OrderItem.product_name, func.sum(OrderItem.quantity).label("total_qty"))
            .group_by(OrderItem.product_name)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
            .all()
        )
        return [{"product_name": r[0], "total_quantity": int(r[1])} for r in results]

    def daily_production_totals(self, days: int = 30) -> List[Dict[str, Any]]:
        end = datetime.now(timezone.utc).date()
        start = end - timedelta(days=days - 1)
        records = self.db.query(MilkRecord).filter(
            MilkRecord.date >= start,
            MilkRecord.date <= end,
        ).all()
        totals: Dict[str, float] = {}
        for r in records:
            d = r.date.isoformat() if hasattr(r.date, "isoformat") else str(r.date)
            totals[d] = totals.get(d, 0.0) + r.available_for_sale
        return [{"date": d, "litres": round(v, 2)} for d, v in sorted(totals.items())]

    def export_sales_csv(self, start_date: str, end_date: str) -> str:
        data = self.sales_by_date_range(start_date, end_date)
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["order_number", "customer_name", "created_at", "total_amount", "payment_method", "order_status"])
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

    def export_production_csv(self, start_date: str, end_date: str) -> str:
        data = self.production_by_date_range(start_date, end_date)
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["cow_id", "date", "session", "yield_litres", "available_for_sale"])
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()