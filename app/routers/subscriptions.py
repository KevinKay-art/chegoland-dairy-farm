"""Subscription routers: recurring milk delivery for customers (HTML + API)."""
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.subscription import Subscription
from app.models.product import Product
from app.models.user import User
from app.utils.security import get_current_user
from app.config import settings
import uuid
from datetime import datetime, timezone

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/account/subscriptions", response_class=HTMLResponse)
async def subscriptions_page(request: Request, db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    subs = db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
    products = db.query(Product).filter(Product.is_active == True).all()
    return templates.TemplateResponse(request, "account/subscriptions.html", {
        "request": request, "user": current_user, "app_name": settings.APP_NAME,
        "subscriptions": subs, "products": products,
    })


@router.post("/account/subscriptions")
async def subscriptions_create(request: Request, product_id: str = Form(...),
                               quantity: int = Form(1), frequency: str = Form("daily"),
                               start_date: str = Form(...), end_date: str = Form(""),
                               notes: str = Form(""),
                               db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    sub = Subscription(
        id=str(uuid.uuid4()), user_id=current_user.id, product_id=product_id,
        quantity=quantity, frequency=frequency, start_date=start_date,
        end_date=end_date or None, is_active=True,
        next_delivery_date=start_date, notes=notes or None,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(sub)
    db.commit()
    return RedirectResponse(url="/account/subscriptions?created=1", status_code=status.HTTP_302_FOUND)


@router.post("/account/subscriptions/{sub_id}/toggle")
async def subscriptions_toggle(sub_id: str, db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    sub = db.query(Subscription).filter(Subscription.id == sub_id,
                                        Subscription.user_id == current_user.id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    sub.is_active = not sub.is_active
    db.commit()
    return RedirectResponse(url="/account/subscriptions", status_code=status.HTTP_302_FOUND)


@router.post("/account/subscriptions/{sub_id}/delete")
async def subscriptions_delete(sub_id: str, db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    sub = db.query(Subscription).filter(Subscription.id == sub_id,
                                        Subscription.user_id == current_user.id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    db.delete(sub)
    db.commit()
    return RedirectResponse(url="/account/subscriptions", status_code=status.HTTP_302_FOUND)


# ===== API Routes =====

api_router = APIRouter(prefix="/api/v1/subscriptions")


@api_router.get("", response_model=list)
async def api_list_subscriptions(db: Session = Depends(get_db),
                                 current_user: User = Depends(get_current_user)):
    query = db.query(Subscription)
    if current_user.role != "admin":
        query = query.filter(Subscription.user_id == current_user.id)
    subs = query.all()
    return [
        {
            "id": s.id, "user_id": s.user_id, "product_id": s.product_id,
            "quantity": s.quantity, "frequency": s.frequency, "start_date": s.start_date,
            "end_date": s.end_date, "is_active": s.is_active,
            "next_delivery_date": s.next_delivery_date, "notes": s.notes,
        }
        for s in subs
    ]


@api_router.post("", status_code=status.HTTP_201_CREATED)
async def api_create_subscription(request: Request, db: Session = Depends(get_db),
                                  current_user: User = Depends(get_current_user)):
    body = await request.json()
    sub = Subscription(
        id=str(uuid.uuid4()), user_id=current_user.id,
        product_id=body.get("product_id"), quantity=body.get("quantity", 1),
        frequency=body.get("frequency", "daily"), start_date=body.get("start_date"),
        end_date=body.get("end_date"), is_active=body.get("is_active", True),
        next_delivery_date=body.get("start_date"), notes=body.get("notes"),
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(sub)
    db.commit()
    return {"id": sub.id, "message": "Subscription created"}


@api_router.put("/{sub_id}")
async def api_update_subscription(sub_id: str, request: Request, db: Session = Depends(get_db),
                                  current_user: User = Depends(get_current_user)):
    query = db.query(Subscription).filter(Subscription.id == sub_id)
    if current_user.role != "admin":
        query = query.filter(Subscription.user_id == current_user.id)
    sub = query.first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    body = await request.json()
    for field in ["quantity", "frequency", "end_date", "is_active", "next_delivery_date", "notes"]:
        if field in body:
            setattr(sub, field, body[field])
    db.commit()
    return {"id": sub.id, "message": "Subscription updated"}


@api_router.delete("/{sub_id}")
async def api_delete_subscription(sub_id: str, db: Session = Depends(get_db),
                                  current_user: User = Depends(get_current_user)):
    query = db.query(Subscription).filter(Subscription.id == sub_id)
    if current_user.role != "admin":
        query = query.filter(Subscription.user_id == current_user.id)
    sub = query.first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    db.delete(sub)
    db.commit()
    return {"message": "Subscription deleted"}

