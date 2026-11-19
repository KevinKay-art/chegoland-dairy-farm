import os
os.environ["DATABASE_URL"] = "sqlite:///./test_dairy.db"
os.environ["MPESA_MOCK_MODE"] = "true"

from sqlalchemy import create_engine
from app.database import Base

from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.payment import Payment

for label, model in [("users", User), ("products", Product), ("orders", Order), ("payments", Payment)]:
    print(f"{label} table indexes:")
    seen = set()
    for idx in model.__table__.indexes:
        key = (idx.name, tuple(c.name for c in idx.columns))
        print(f"  - {idx.name}: {[c.name for c in idx.columns]}  (dup={key in seen})")
        seen.add(key)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_dairy.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

print("\ncreate_all #1 (fresh DB)")
Base.metadata.create_all(bind=engine)
print("create_all #1 done")

