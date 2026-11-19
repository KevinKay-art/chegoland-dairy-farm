"""Admin dashboard routers: HTML pages + API for admin operations."""

from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.order import Order
from app.models.product import Product
from app.models.cow import Cow
from app.models.user import User
from app.models.milk_record import MilkRecord
from app.models.payment import Payment
from app.services.order_service import OrderService
from app.services.inventory_service import InventoryService
from app.services.report_service import ReportService
from app.utils.security import require_role, get_current_user
from app.config import settings
import csv
import io
import jinja2

router = APIRouter()
templates = Jinja2Templates(env=jinja2.Environment(
    loader=jinja2.FileSystemLoader("app/templates"),
    autoescape=jinja2.select_autoescape(),
    cache_size=0,  # Disable template cache to avoid weakref key hash issues
))


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db),
                          current_user: User = Depends(require_role(["admin"]))):
    order_service = OrderService(db)
    inventory_service = InventoryService(db)
    report_service = ReportService(db)

    today_sales = order_service.get_today_sales()
    pending_orders = order_service.get_pending_orders_count()
    low_stock = inventory_service.get_low_stock()
    total_cows = db.query(Cow).count()
    total_products = db.query(Product).count()
    total_orders = db.query(Order).count()

    from datetime import datetime
    now = datetime.now()
    monthly_revenue = order_service.get_monthly_revenue(now.year, now.month)
    production = report_service.daily_production_totals(days=7)
    top_products = report_service.top_products(limit=5)

    return templates.TemplateResponse(request, "admin/dashboard.html", {
        "request": request, "user": current_user, "app_name": settings.APP_NAME,
        "today_sales": today_sales, "monthly_revenue": monthly_revenue,
        "pending_orders": pending_orders, "low_stock": low_stock,
        "total_cows": total_cows, "total_products": total_products,
        "total_orders": total_orders,
        "production": production, "top_products": top_products,
    })


@router.get("/admin/products", response_class=HTMLResponse)
async def admin_products(request: Request, db: Session = Depends(get_db),
                         current_user: User = Depends(require_role(["admin"]))):
    products = db.query(Product).all()
    return templates.TemplateResponse(request, "admin/products.html", {
        "request": request, "user": current_user, "app_name": settings.APP_NAME, "products": products,
    })


@router.get("/admin/orders", response_class=HTMLResponse)
async def admin_orders(request: Request, db: Session = Depends(get_db),
                       current_user: User = Depends(require_role(["admin"]))):
    order_service = OrderService(db)
    orders = order_service.list_orders()
    return templates.TemplateResponse(request, "admin/orders.html", {
        "request": request, "user": current_user, "app_name": settings.APP_NAME, "orders": orders,
    })


@router.get("/admin/cows", response_class=HTMLResponse)
async def admin_cows(request: Request, db: Session = Depends(get_db),
                     current_user: User = Depends(require_role(["admin"]))):
    cows = db.query(Cow).all()
    return templates.TemplateResponse(request, "admin/cows.html", {
        "request": request, "user": current_user, "app_name": settings.APP_NAME, "cows": cows,
    })


@router.get("/admin/milk", response_class=HTMLResponse)
async def admin_milk(request: Request, db: Session = Depends(get_db),
                     current_user: User = Depends(require_role(["admin"]))):
    records = db.query(MilkRecord).order_by(MilkRecord.date.desc()).limit(50).all()
    cows = db.query(Cow).all()
    return templates.TemplateResponse(request, "admin/milk.html", {
        "request": request, "user": current_user, "app_name": settings.APP_NAME,
        "records": records, "cows": cows,
    })


@router.get("/admin/customers", response_class=HTMLResponse)
async def admin_customers(request: Request, db: Session = Depends(get_db),
                          current_user: User = Depends(require_role(["admin"]))):
    customers = db.query(User).filter(User.role == "customer").all()
    return templates.TemplateResponse(request, "admin/customers.html", {
        "request": request, "user": current_user, "app_name": settings.APP_NAME, "customers": customers,
    })


@router.get("/admin/reports", response_class=HTMLResponse)
async def admin_reports(request: Request, current_user: User = Depends(require_role(["admin"]))):
    return templates.TemplateResponse(request, "admin/reports.html", {
        "request": request, "user": current_user, "app_name": settings.APP_NAME,
    })


@router.get("/admin/invoice/{order_id}", response_class=HTMLResponse)
async def admin_invoice(request: Request, order_id: str, db: Session = Depends(get_db),
                        current_user: User = Depends(require_role(["admin"]))):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return templates.TemplateResponse(request, "admin/invoice.html", {
        "request": request, "user": current_user, "app_name": settings.APP_NAME, "order": order,
    })


@router.get("/api/v1/admin/stats")
async def api_admin_stats(db: Session = Depends(get_db),
                          current_user: User = Depends(require_role(["admin"]))):
    order_service = OrderService(db)
    from datetime import datetime
    now = datetime.now()
    return {
        "today_sales": order_service.get_today_sales(),
        "monthly_revenue": order_service.get_monthly_revenue(now.year, now.month),
        "pending_orders": order_service.get_pending_orders_count(),
        "total_cows": db.query(Cow).count(),
        "total_products": db.query(Product).count(),
        "total_orders": db.query(Order).count(),
    }


@router.get("/api/v1/admin/production-chart")
async def api_production_chart(days: int = 30, db: Session = Depends(get_db),
                               current_user: User = Depends(require_role(["admin"]))):
    report_service = ReportService(db)
    return report_service.daily_production_totals(days=days)


@router.get("/api/v1/admin/top-products")
async def api_top_products(limit: int = 10, db: Session = Depends(get_db),
                           current_user: User = Depends(require_role(["admin"]))):
    report_service = ReportService(db)
    return report_service.top_products(limit=limit)


@router.get("/api/v1/admin/reports/sales/csv")
async def api_export_sales_csv(start_date: str, end_date: str, db: Session = Depends(get_db),
                               current_user: User = Depends(require_role(["admin"]))):
    report_service = ReportService(db)
    csv_content = report_service.export_sales_csv(start_date, end_date)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=sales_{start_date}_to_{end_date}.csv"},
    )