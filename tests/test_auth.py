from app.services.auth_service import AuthService
from app.models.user import User


def test_authenticate_user(client, db):
    service = AuthService(db)
    user = service.authenticate_user("admin@test.com", "Admin123!")
    assert user is not None
    assert user.role == "admin"

    wrong = service.authenticate_user("admin@test.com", "wrongpassword")
    assert wrong is None


def test_api_login(client):
    resp = client.post("/api/v1/auth/login", data={
        "email": "admin@test.com",
        "password": "Admin123!"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_api_login_wrong_password(client):
    resp = client.post("/api/v1/auth/login", data={
        "email": "admin@test.com",
        "password": "wrongpassword"
    })
    assert resp.status_code == 401


def test_api_register(client):
    resp = client.post("/api/v1/auth/register", data={
        "email": "newuser@test.com",
        "password": "NewPass123!",
        "full_name": "New User",
        "phone": "+254700000001"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "newuser@test.com"


def test_api_register_duplicate(client):
    resp = client.post("/api/v1/auth/register", data={
        "email": "admin@test.com",
        "password": "Admin123!",
        "full_name": "Duplicate",
    })
    assert resp.status_code == 400


def test_api_me(client, admin_token):
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "admin@test.com"