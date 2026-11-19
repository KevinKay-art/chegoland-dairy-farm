import os
os.environ["DATABASE_URL"] = "sqlite:///./test_dairy.db"
os.environ["MPESA_MOCK_MODE"] = "true"
os.environ["TESTING"] = "true"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app
from app.database import get_db
from app.services.auth_service import hash_password
from app.models.user import User
import uuid

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_dairy.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        # Create admin user
        admin = User(
            id=str(uuid.uuid4()),
            email="admin@test.com",
            hashed_password=hash_password("Admin123!"),
            full_name="Test Admin",
            role="admin",
            is_active=True,
            is_verified=True,
        )
        session.add(admin)
        session.commit()
        transaction.commit()

        yield session
    finally:
        session.close()
        connection.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_token(client):
    resp = client.post("/api/v1/auth/login", data={
        "email": "admin@test.com",
        "password": "Admin123!"
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]