# CHEGOLAND AGRI-EMPIRE LTD DAIRY FARM AND SHOP

A complete, production-ready dairy farm web application built with **FastAPI**, **SQLAlchemy 2.x**, **Alembic**, **Jinja2**, **Tailwind CSS**, **Alpine.js**, and **Chart.js**. Customers browse and buy fresh milk and dairy products online; the farmer manages products, orders, cows, and milk production from a secure admin dashboard.

**Farm location:** Kapcholyo, Kaplong and its environs. The herd is managed under zero-grazing units with daily morning and evening milk records.

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- `pip` and `venv`

### 1. Clone & Create Virtual Environment
```bash
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```
At minimum, set `ADMIN_PASSWORD` and `SECRET_KEY`. M-Pesa keys are optional — the app runs in **mock mode** by default.

### 4. Run Migrations
```bash
alembic upgrade head
```

### 5. Seed the Database
```bash
python scripts/seed.py
```
This creates:
- 1 admin (`admin@chegoland.com`)
- 8 sample cows (Friesian, Ayrshire, Jersey, Guernsey)
- 9 products (milk first: fresh milk, mala, yoghurt, ghee, butter, cheese, eggs, manure)
- 30 days of milk production records
- Sample customer and orders

### 6. Start the Server
```bash
uvicorn app.main:app --reload
```
Visit **http://localhost:8000** — the site is live with seed data.

## 🔐 Default Admin Login
| Field | Value |
|-------|-------|
| Email | `admin@chegoland.com` |
| Password | From `.env` `ADMIN_PASSWORD` (default `Admin123!`) |

Access the admin dashboard at **/admin**.

## 🧪 Running Tests
```bash
pytest
```
All tests must pass. Tests cover auth, product listing, cart, checkout & stock reduction, order status flow, M-Pesa callback, and admin access control.

## 📦 Project Structure
```
chegoland/
├── app/
│   ├── main.py              # FastAPI app, middleware, routers, error handlers
│   ├── config.py            # Pydantic-settings (reads .env)
│   ├── database.py          # SQLAlchemy engine, session, Base
│   ├── models/              # SQLAlchemy models (user, cow, product, order, ...)
│   ├── schemas/             # Pydantic v2 schemas
│   ├── routers/             # HTML + /api/v1 routes (auth, public, products, cart, orders, payments, admin, cows, milk, subscriptions, health_records, contact_messages)
│   ├── services/            # auth, order, mpesa, inventory, notification, report
│   ├── utils/               # security (JWT, roles), CSRF, rate limit, image validation
│   ├── templates/           # Jinja2 server-rendered HTML
│   └── static/              # CSS, JS, images, uploads
├── alembic/                 # Database migrations
├── scripts/seed.py          # Seed data
├── tests/                   # pytest suite
├── requirements.txt         # Pinned dependencies
├── .env.example             # Environment variable template
├── Dockerfile               # Multi-stage, non-root
├── docker-compose.yml       # App + Postgres
├── Procfile                 # Render/Railway
├── render.yaml              # Render deployment config
├── README.md                # This file
└── DEPLOY.md                # Production deployment guide
```

## 🛠 Features

### Customer Storefront
- Home page: hero banner, live cow carousel, featured products, stats, testimonials, delivery areas
- Shop: search, category filter, sort, pagination
- Product detail with "Add to Cart" (AJAX, no reload)
- Cart: session-based, quantity updates, removal, subtotal/delivery/total
- Checkout: delivery address, date/time slot, payment method (M-Pesa or Cash on Delivery)
- Order confirmation & tracking by order number
- Subscriptions: recurring daily/weekly milk delivery from account page
- About & Contact pages (contact form saves to DB)

### Admin Dashboard (/admin)
- Overview: today's sales, monthly revenue, pending orders, cows, low-stock alerts, charts
- Products CRUD with image upload
- Orders: list, update status, print invoice
- Cows CRUD: tag, name, breed, DOB, photo, status, health records
- Milk production: morning/evening yield per cow, daily totals
- Customers & subscriptions management
- Reports: sales/production by date range, CSV export

### Payments
- M-Pesa Daraja STK Push (sandbox) with callback endpoint
- Mock mode when keys are absent (full demo flow locally)
- Cash on Delivery option
- Payment status transitions: pending → completed/failed

### API
- Full REST API under `/api/v1` with auto docs at `/docs`
- HTML pages and JSON API share the same service layer

### Security
- JWT in HttpOnly cookies, bcrypt password hashing
- Role-based access (admin/customer)
- CSRF protection, rate limiting on login, CORS, security headers
- Image upload validation (type, size, safe filenames)

## 🚀 Deployment
See **DEPLOY.md** for Render/Railway and VPS (Nginx + Certbot + systemd) instructions.

### Docker
```bash
docker-compose up --build
```

## 📄 License
MIT