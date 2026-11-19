"""Chegoland dairy farm storefront and management application."""

from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import text
from app.database import SessionLocal
from app.config import settings
from app import models
from app.routers import auth, public, products, cart, orders, payments, admin, cows, milk, subscriptions, health_records, contact_messages
from app.services.auth_service import AuthService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dairy")
APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
TEMPLATES_DIR = APP_DIR / "templates"

app = FastAPI(
    title=settings.FARM_NAME,
    description=settings.APP_DESCRIPTION,
    version="1.0.0",
)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    https_only=settings.COOKIE_SECURE,
    same_site="lax",
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if settings.COOKIE_SECURE:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(STATIC_DIR / "uploads")), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(auth.api_router)
app.include_router(public.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(admin.router)
app.include_router(cows.router)
app.include_router(milk.router)
app.include_router(subscriptions.router)
app.include_router(subscriptions.api_router)
app.include_router(health_records.router)
app.include_router(contact_messages.router)


@app.get("/health")
async def health():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"status": "healthy", "app": settings.FARM_NAME}


# Seed admin user on startup if not exists (skipped during tests)
@app.on_event("startup")
def seed_admin():
    import os
    if os.environ.get("TESTING") == "true":
        return
    db = SessionLocal()
    try:
        auth_service = AuthService(db)
        if not auth_service.get_user_by_email(settings.ADMIN_EMAIL):
            auth_service.create_user(
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
                full_name="Farm Administrator",
                role="admin",
            )
            logger.info(f"Seeded admin user: {settings.ADMIN_EMAIL}")
    finally:
        db.close()


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    if request.url.path.startswith("/api/"):
        return JSONResponse({"error": "Not found"}, status_code=404)
    return templates.TemplateResponse(request, "errors/404.html",
        {"request": request, "app_name": settings.FARM_NAME},
        status_code=404,
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    logger.error("Server error while handling %s: %s", request.url.path, exc)
    if request.url.path.startswith("/api/"):
        return JSONResponse({"error": "Internal server error"}, status_code=500)
    return templates.TemplateResponse(request, "errors/500.html",
        {"request": request, "app_name": settings.FARM_NAME},
        status_code=500,
    )