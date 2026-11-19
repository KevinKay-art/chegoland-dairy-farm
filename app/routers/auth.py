"""Auth routers: login, register, logout, profile (HTML + API)."""

from fastapi import APIRouter, Request, Form, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import SessionLocal, get_db
from app.config import settings
from app.services.auth_service import AuthService, create_access_token, verify_password, hash_password
from app.models.user import User
from app.utils.security import get_current_user_optional, get_current_user, require_role
from app.utils.csrf import generate_csrf_token, validate_csrf_token
from app.utils.rate_limit import RateLimiter
from app.config import settings
import time

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

rate_limiter = RateLimiter(max_attempts=5, window_seconds=300)


def get_templates():
    return templates


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "auth/login.html", {"request": request, "csrf_token": generate_csrf_token(request)})


@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...),
                csrf_token: str = Form(...), db: Session = Depends(get_db)):
    # Rate limiting
    client_ip = request.client.host
    if not rate_limiter.check(f"login:{client_ip}"):
        raise HTTPException(status_code=429, detail="Too many login attempts. Try again later.")

    # CSRF validation
    if not validate_csrf_token(request, csrf_token):
        raise HTTPException(status_code=400, detail="Invalid CSRF token")

    auth_service = AuthService(db)
    user = auth_service.authenticate_user(email, password)
    if not user:
        return templates.TemplateResponse(request, "auth/login.html", {
            "request": request, "error": "Invalid email or password", "csrf_token": generate_csrf_token(request)
        })

    token = create_access_token(data={"sub": user.email, "role": user.role})
    # Farm admins go straight to the farm admin dashboard; customers to the storefront
    redirect_url = "/admin" if user.role == "admin" else "/"
    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        secure=False,  # True in production with HTTPS
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request, "auth/register.html", {"request": request, "csrf_token": generate_csrf_token(request)})


@router.post("/register")
async def register(request: Request, email: str = Form(...), password: str = Form(...),
                   full_name: str = Form(...), phone: str = Form(""),
                   csrf_token: str = Form(...), db: Session = Depends(get_db)):
    if not validate_csrf_token(request, csrf_token):
        raise HTTPException(status_code=400, detail="Invalid CSRF token")

    auth_service = AuthService(db)
    if auth_service.get_user_by_email(email):
        return templates.TemplateResponse(request, "auth/register.html", {
            "request": request, "error": "Email already registered", "csrf_token": generate_csrf_token(request)
        })

    auth_service.create_user(email=email, password=password, full_name=full_name, phone=phone or None)
    return RedirectResponse(url="/login?registered=1", status_code=status.HTTP_302_FOUND)


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response


@router.get("/account", response_class=HTMLResponse)
async def account_page(request: Request, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request, "account/dashboard.html", {
        "request": request, "user": current_user, "csrf_token": generate_csrf_token(request)
    })


# ===== API Routes =====

api_router = APIRouter(prefix="/api/v1/auth")


@api_router.post("/login")
async def api_login(email: str = Form(...), password: str = Form(...),
                    db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.email, "role": user.role, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "email": user.email, "role": user.role, "full_name": user.full_name}}


@api_router.post("/register")
async def api_register(email: str = Form(...), password: str = Form(...),
                       full_name: str = Form(...), phone: str = Form(""),
                       db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    if auth_service.get_user_by_email(email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = auth_service.create_user(email=email, password=password, full_name=full_name, phone=phone or None)
    return {"id": user.id, "email": user.email, "role": user.role, "full_name": user.full_name}


@api_router.get("/me")
async def api_me(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"id": current_user.id, "email": current_user.email, "role": current_user.role, "full_name": current_user.full_name}