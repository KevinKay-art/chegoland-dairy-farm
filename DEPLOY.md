# Deployment Guide — Chegoland

Production deployment options for Chegoland. Choose **(a)** Render/Railway (PaaS, easiest) or **(b)** a VPS with Nginx + Certbot HTTPS + systemd.

Prerequisites for both:
- A `.env` file with production values (never commit it)
- A `SECRET_KEY` of at least 32 random characters
- A strong `ADMIN_PASSWORD` (at least 12 characters)
- M-Pesa sandbox or production keys (optional; mock mode works without them)

## (a) Render / Railway (PaaS — one-click)

### 1. Prepare the repo
Ensure these files are committed: `requirements.txt`, `Procfile`, `render.yaml`, `Dockerfile`, `docker-compose.yml`, `alembic/`, `scripts/seed.py`, `app/`.

### 2. Set environment variables
On Render/Railway, add the following env vars:

| Variable | Example Value | Notes |
|----------|---------------|-------|
| `DATABASE_URL` | `postgresql+psycopg2://user:pass@host:5432/db` | Provided by Render/Railway PostgreSQL |
| `SECRET_KEY` | `abc123...` | ≥32 random chars |
| `ADMIN_EMAIL` | `admin@chegoland.com` | |
| `ADMIN_PASSWORD` | `Str0ngP@ssw0rd!` | ≥12 chars |
| `MPESA_ENVIRONMENT` | `sandbox` | or `production` |
| `MPESA_CALLBACK_URL` | `https://yourdomain.com/api/v1/payments/mpesa/callback` | Required for real M-Pesa |
| `MPESA_MOCK_MODE` | `false` | `false` with real keys; `true` for demo |
| `COOKIE_SECURE` | `true` | Required with HTTPS |
| `CORS_ALLOWED_ORIGINS` | `https://yourdomain.com` | |
| `ALLOWED_HOSTS` | `yourdomain.com` | |

### 3. Deploy
- **Render**: connect your GitHub repo, use `render.yaml` (included). Build runs `pip install -r requirements.txt && alembic upgrade head && python scripts/seed.py`. Start uses Gunicorn with Uvicorn workers.
- **Railway**: connect your GitHub repo, add PostgreSQL, set env vars, use the `Procfile` start command.

### 4. Run migrations & seed (first deploy)
Render does this automatically via `render.yaml` buildCommand. If running manually:
```bash
alembic upgrade head
python scripts/seed.py
```

### 5. Set the M-Pesa callback URL
In the Safaricom Daraja developer portal, set your STK Push callback URL to:
```
https://yourdomain.com/api/v1/payments/mpesa/callback
```

## (b) VPS with Nginx + Certbot HTTPS + systemd

### 1. Provision the server
- Ubuntu 22.04+ VPS
- Root or sudo user
- Domain name pointing to the server IP

### 2. Install dependencies
```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip nginx postgresql postgresql-contrib certbot python3-certbot-nginx git
```

### 3. Create a deploy user
```bash
sudo useradd -m -s /bin/bash chegoland
sudo usermod -aG sudo chegoland
sudo su - chegoland
```

### 4. Clone the repo
```bash
git clone <your-repo-url> ~/chegoland
cd ~/chegoland
```

### 5. Set up Python virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Configure environment
```bash
cp .env.example .env
nano .env
```
Set production values:
```
DATABASE_URL=postgresql+psycopg2://chegoland:password@localhost:5432/chegoland
SECRET_KEY=<32+ random chars>
ADMIN_EMAIL=admin@chegoland.com
ADMIN_PASSWORD=<strong password>
COOKIE_SECURE=True
MPESA_MOCK_MODE=false
MPESA_CALLBACK_URL=https://yourdomain.com/api/v1/payments/mpesa/callback
CORS_ALLOWED_ORIGINS=https://yourdomain.com
ALLOWED_HOSTS=yourdomain.com
```

### 7. Set up PostgreSQL
```bash
sudo -u postgres createuser chegoland
sudo -u postgres createdb -O chegoland chegoland
sudo -u postgres psql -c "ALTER USER chegoland PASSWORD 'password';"
```
Update `DATABASE_URL` in `.env` with the correct credentials.

### 8. Run migrations & seed
```bash
source .venv/bin/activate
alembic upgrade head
python scripts/seed.py
```

### 9. Create systemd service
Create `/etc/systemd/system/chegoland.service`:
```ini
[Unit]
Description=Chegoland Dairy Farm
After=network.target

[Service]
User=chegoland
Group=chegoland
WorkingDirectory=/home/chegoland/chegoland
Environment="PATH=/home/chegoland/chegoland/.venv/bin"
EnvironmentFile=/home/chegoland/chegoland/.env
ExecStart=/home/chegoland/chegoland/.venv/bin/gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 127.0.0.1:8000 app.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now chegoland
```

### 10. Configure Nginx
Create `/etc/nginx/sites-available/chegoland`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/chegoland/chegoland/app/static/;
    }

    location /uploads/ {
        alias /home/chegoland/chegoland/app/static/uploads/;
    }
}

server {
    if ($host = yourdomain.com) {
        return 301 https://$host$request_uri;
    }
    listen 80;
    server_name yourdomain.com;
    return 404;
}
```

```bash
sudo ln -s /etc/nginx/sites-available/chegoland /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 11. Install SSL (Certbot)
```bash
sudo certbot --nginx -d yourdomain.com
```
Follow the prompts to enable HTTPS and redirect HTTP to HTTPS.

### 12. Verify
- Visit `https://yourdomain.com` — the storefront loads
- Visit `https://yourdomain.com/docs` — API docs
- Visit `https://yourdomain.com/admin` — admin dashboard (login with admin credentials)
- Set the M-Pesa callback URL to `https://yourdomain.com/api/v1/payments/mpesa/callback`

### 13. Ongoing maintenance
```bash
# Restart after code changes
sudo systemctl restart chegoland

# View logs
sudo journalctl -u chegoland -f

# Renew SSL (auto via certbot timer)
sudo certbot renew --dry-run
```

---

## Environment Variable Reference

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `FARM_NAME` | `CHEGOLAND AGRI-EMPIRE LTD DAIRY FARM AND SHOP` | No | Display name (configurable via .env) |
| `SECRET_KEY` | — | Yes | JWT signing key (≥32 chars) |
| `DATABASE_URL` | `sqlite:///./dairy_farm.db` | No | SQLite for dev, PostgreSQL for prod |
| `ADMIN_EMAIL` | `admin@chegoland.com` | No | Seeded admin email |
| `ADMIN_PASSWORD` | — | Yes | Seeded admin password (≥12 chars) |
| `MPESA_MOCK_MODE` | `true` | No | `true` = demo mode without keys |
| `MPESA_CALLBACK_URL` | — | Yes (prod) | M-Pesa STK Push callback endpoint |
| `COOKIE_SECURE` | `false` | No | `true` in production with HTTPS |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:8000` | No | Comma-separated allowed origins |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | No | Allowed host headers |