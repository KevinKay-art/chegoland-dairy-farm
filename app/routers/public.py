"""Public pages: home, shop, product detail, cows, about, contact, cart, checkout, order tracking."""

from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Product
from app.models.cow import Cow
from app.models.order import Order
from app.models.user import User
from app.models.milk_record import MilkRecord
from app.utils.security import get_current_user_optional
from app.config import settings
from datetime import datetime, timedelta, timezone

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user_optional)):
    featured = db.query(Product).filter(Product.is_active == True, Product.is_featured == True).limit(8).all()
    cows = db.query(Cow).filter(Cow.status == "lactating").limit(6).all()
    total_cows = db.query(Cow).count()
    total_customers = db.query(User).filter(User.role == "customer").count()

    # Live stat: litres produced this month (from the database)
    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()
    if now.month == 12:
        end_of_month = now.replace(year=now.year + 1, month=1, day=1).date()
    else:
        end_of_month = now.replace(month=now.month + 1, day=1).date()
    end_of_month = end_of_month - timedelta(days=1)
    monthly_litres = db.query(MilkRecord).filter(
        MilkRecord.date >= start_of_month,
        MilkRecord.date <= end_of_month,
    ).with_entities(MilkRecord.available_for_sale).all()
    monthly_production = round(sum(r[0] for r in monthly_litres), 1)

    # Cart count from session
    cart = request.session.get("cart", {})
    cart_count = sum(item.get("quantity", 0) for item in cart.values())

    return templates.TemplateResponse(request, "home.html", {
        "request": request, "featured": featured, "cows": cows,
        "total_cows": total_cows, "total_customers": total_customers,
        "monthly_production": monthly_production,
        "cart_count": cart_count,
        "user": current_user, "app_name": settings.APP_NAME,
    })


@router.get("/shop", response_class=HTMLResponse)
async def shop(request: Request, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user_optional),
               search: str = Query(None), category: str = Query(None),
               sort: str = Query("name"), page: int = Query(1, ge=1)):
    query = db.query(Product).filter(Product.is_active == True)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if category:
        query = query.filter(Product.category == category)
    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.name.asc())

    per_page = 12
    total = query.count()
    products = query.offset((page - 1) * per_page).limit(per_page).all()
    categories = [c[0] for c in db.query(Product.category).distinct().all()]
    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse(request, "shop.html", {
        "request": request, "products": products, "categories": categories,
        "current_category": category, "search": search, "sort": sort,
        "page": page, "total_pages": total_pages, "total": total,
        "user": current_user, "app_name": settings.APP_NAME,
    })


@router.get("/product/{slug}", response_class=HTMLResponse)
async def product_detail(request: Request, slug: str, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user_optional)):
    product = db.query(Product).filter(Product.slug == slug, Product.is_active == True).first()
    if not product:
        return templates.TemplateResponse(request, "errors/404.html", {"request": request}, status_code=404)
    return templates.TemplateResponse(request, "product_detail.html", {
        "request": request, "product": product, "user": current_user, "app_name": settings.APP_NAME,
    })


@router.get("/cows", response_class=HTMLResponse)
async def cows_gallery(request: Request, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user_optional)):
    cows = db.query(Cow).all()
    return templates.TemplateResponse(request, "cows.html", {
        "request": request, "cows": cows, "user": current_user, "app_name": settings.APP_NAME,
    })


@router.get("/cows/{cow_id}", response_class=HTMLResponse)
async def cow_profile(request: Request, cow_id: str, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user_optional)):
    cow = db.query(Cow).filter(Cow.id == cow_id).first()
    if not cow:
        return templates.TemplateResponse(request, "errors/404.html", {"request": request}, status_code=404)
    from app.models.milk_record import MilkRecord
    records = db.query(MilkRecord).filter(MilkRecord.cow_id == cow_id).order_by(MilkRecord.date.desc()).limit(10).all()
    return templates.TemplateResponse(request, "cow_detail.html", {
        "request": request, "cow": cow, "records": records, "user": current_user, "app_name": settings.APP_NAME,
    })


@router.get("/about", response_class=HTMLResponse)
async def about(request: Request, current_user: User = Depends(get_current_user_optional)):
    return templates.TemplateResponse(request, "about.html", {"request": request, "user": current_user, "app_name": settings.APP_NAME})


@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request, current_user: User = Depends(get_current_user_optional)):
    return templates.TemplateResponse(request, "contact.html", {"request": request, "user": current_user, "app_name": settings.APP_NAME})


@router.post("/contact")
async def contact_submit(request: Request, name: str = Form(...), email: str = Form(...),
                         phone: str = Form(""), message: str = Form(...),
                         db: Session = Depends(get_db)):
    import uuid
    from datetime import datetime, timezone
    from app.models.contact import ContactMessage
    msg = ContactMessage(
        id=str(uuid.uuid4()),
        name=name, email=email, phone=phone, message=message,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(msg)
    db.commit()
    return templates.TemplateResponse(request, "contact.html", {
        "request": request, "success": "Thank you! Your message has been sent.", "app_name": settings.APP_NAME,
    })


@router.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request, current_user: User = Depends(get_current_user_optional)):
    cart = request.session.get("cart", {})
    return templates.TemplateResponse(request, "cart.html", {
        "request": request, "cart": cart, "user": current_user, "app_name": settings.APP_NAME,
    })


@router.get("/checkout", response_class=HTMLResponse)
async def checkout_page(request: Request, current_user: User = Depends(get_current_user_optional)):
    cart = request.session.get("cart", {})
    if not cart:
        return RedirectResponse(url="/cart", status_code=302)
    return templates.TemplateResponse(request, "checkout.html", {
        "request": request, "cart": cart, "user": current_user, "app_name": settings.APP_NAME,
    })


@router.get("/order/{order_number}", response_class=HTMLResponse)
async def order_tracking(request: Request, order_number: str, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user_optional)):
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order:
        return templates.TemplateResponse(request, "errors/404.html", {"request": request}, status_code=404)
    return templates.TemplateResponse(request, "order_tracking.html", {
        "request": request, "order": order, "user": current_user, "app_name": settings.APP_NAME,
    })


@router.get("/order-confirmation/{order_id}", response_class=HTMLResponse)
async def order_confirmation(request: Request, order_id: str, db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user_optional)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return templates.TemplateResponse(request, "errors/404.html", {"request": request}, status_code=404)
    return templates.TemplateResponse(request, "order_confirmation.html", {
        "request": request, "order": order, "user": current_user, "app_name": settings.APP_NAME,
    })