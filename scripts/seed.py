"""Seed script: creates admin, cows, products, milk records, customers, orders."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, date, timedelta
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.cow import Cow
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.milk_record import MilkRecord
from app.models.payment import Payment
from app.models.contact import ContactMessage
from app.models.health_record import HealthRecord
from app.models.subscription import Subscription
from app.services.auth_service import hash_password
import uuid


def seed():
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)

        admin_email = os.getenv("ADMIN_EMAIL", "admin@chegoland.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "Admin123!")

        existing = db.query(User).filter(User.email == admin_email).first()
        if not existing:
            admin = User(
                id=str(uuid.uuid4()),
                email=admin_email,
                hashed_password=hash_password(admin_password),
                full_name="Farm Administrator",
                role="admin",
                is_active=True,
                is_verified=True,
                created_at=datetime.now().isoformat(),
            )
            db.add(admin)
            print(f"Created admin: {admin_email}")
        else:
            print(f"Admin already exists: {admin_email}")

        cows_data = [
            {"tag_number": "CG001", "name": "Daisy", "breed": "Friesian", "daily_avg_yield": 28.5, "status": "lactating"},
            {"tag_number": "CG002", "name": "Bella", "breed": "Ayrshire", "daily_avg_yield": 22.0, "status": "lactating"},
            {"tag_number": "CG003", "name": "Molly", "breed": "Jersey", "daily_avg_yield": 18.5, "status": "lactating"},
            {"tag_number": "CG004", "name": "Lucy", "breed": "Guernsey", "daily_avg_yield": 20.0, "status": "lactating"},
            {"tag_number": "CG005", "name": "Clover", "breed": "Friesian", "daily_avg_yield": 30.0, "status": "lactating"},
            {"tag_number": "CG006", "name": "Buttercup", "breed": "Ayrshire", "daily_avg_yield": 24.0, "status": "dry"},
            {"tag_number": "CG007", "name": "Honey", "breed": "Jersey", "daily_avg_yield": 16.0, "status": "pregnant"},
            {"tag_number": "CG008", "name": "Rosie", "breed": "Guernsey", "daily_avg_yield": 0.0, "status": "sick"},
        ]

        for cdata in cows_data:
            existing = db.query(Cow).filter(Cow.tag_number == cdata["tag_number"]).first()
            if not existing:
                cow = Cow(
                    id=str(uuid.uuid4()),
                    photo_url=f"https://images.unsplash.com/photo-1590588292422-8399e897c50b?w=400&auto=format&fit=crop&seed={cdata['tag_number']}",
                    **cdata
                )
                db.add(cow)
        print("Created 8 cows")

        products_data = [
            {"name": "Fresh Whole Milk", "slug": "fresh-whole-milk", "description": "Fresh pasteurized whole milk from our happy cows", "category": "milk", "price": 120.0, "unit": "litre", "stock_quantity": 100, "is_featured": True},
            {"name": "Fermented Milk (Mala)", "slug": "fermented-milk-mala", "description": "Traditional fermented milk, thick and creamy", "category": "milk", "price": 100.0, "unit": "500ml", "stock_quantity": 80, "is_featured": True},
            {"name": "Natural Yoghurt", "slug": "natural-yoghurt", "description": "Creamy natural yoghurt with live cultures", "category": "dairy", "price": 90.0, "unit": "500ml", "stock_quantity": 60, "is_featured": True},
            {"name": "Ghee", "slug": "ghee", "description": "Pure clarified butter, golden and aromatic", "category": "dairy", "price": 450.0, "unit": "500ml", "stock_quantity": 40, "is_featured": False},
            {"name": "Butter", "slug": "butter", "description": "Fresh churned butter, salted", "category": "dairy", "price": 350.0, "unit": "250g", "stock_quantity": 50, "is_featured": False},
            {"name": "Cheese", "slug": "cheese", "description": "Fresh farm cheese, mild flavor", "category": "dairy", "price": 280.0, "unit": "200g", "stock_quantity": 30, "is_featured": False},
            {"name": "Farm Eggs", "slug": "farm-eggs", "description": "Free-range farm eggs, crate of 30", "category": "eggs", "price": 300.0, "unit": "crate", "stock_quantity": 20, "is_featured": False},
            {"name": "Manure/Fertilizer", "slug": "manure-fertilizer", "description": "Organic cow manure for farming", "category": "manure", "price": 50.0, "unit": "kg", "stock_quantity": 200, "is_featured": False},
        ]

        for pdata in products_data:
            existing = db.query(Product).filter(Product.slug == pdata["slug"]).first()
            if not existing:
                product = Product(
                    id=str(uuid.uuid4()),
                    image_url=f"https://images.unsplash.com/photo-1564947779-46498e5a2a8c?w=400&auto=format&fit=crop&seed={pdata['slug']}",
                    **pdata
                )
                db.add(product)
        print("Created products")

        db.commit()

        cows = db.query(Cow).all()
        products = db.query(Product).all()
        today = date.today()
        for i in range(30):
            d = today - timedelta(days=i)
            for cow in cows:
                if cow.status == "lactating":
                    morning = round(12.0 + (i % 5) * 1.5, 1)
                    evening = round(10.0 + (i % 4) * 1.2, 1)
                    record = MilkRecord(
                        id=str(uuid.uuid4()),
                        cow_id=cow.id,
                        date=d,
                        session="morning",
                        yield_litres=morning,
                        used_by_calves=round(morning * 0.1, 1),
                        spoiled=0.0,
                        available_for_sale=round(morning * 0.9, 1),
                    )
                    db.add(record)
                    record2 = MilkRecord(
                        id=str(uuid.uuid4()),
                        cow_id=cow.id,
                        date=d,
                        session="evening",
                        yield_litres=evening,
                        used_by_calves=round(evening * 0.1, 1),
                        spoiled=0.0,
                        available_for_sale=round(evening * 0.9, 1),
                    )
                    db.add(record2)
        db.commit()
        print("Created milk records")

        customer = db.query(User).filter(User.role == "customer").first()
        if not customer:
            customer = User(
                id=str(uuid.uuid4()),
                email="customer@example.com",
                hashed_password=hash_password("Customer123!"),
                full_name="John Customer",
                role="customer",
                phone="+254700000000",
                address="Nairobi, Kenya",
                city="Nairobi",
                created_at=datetime.now().isoformat(),
            )
            db.add(customer)
            db.commit()
            print("Created sample customer")

        milk_product = db.query(Product).filter(Product.slug == "fresh-whole-milk").first()
        mala_product = db.query(Product).filter(Product.slug == "fermented-milk-mala").first()

        if milk_product and customer:
            for i in range(5):
                order_date = today - timedelta(days=i * 6)
                order = Order(
                    id=str(uuid.uuid4()),
                    order_number=f"CG{order_date.strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}",
                    user_id=customer.id,
                    customer_name=customer.full_name,
                    customer_phone=customer.phone,
                    customer_email=customer.email,
                    delivery_address=customer.address,
                    delivery_date=order_date.isoformat(),
                    delivery_time_slot="Morning (8am-12pm)",
                    payment_method="cash_on_delivery",
                    payment_status="paid",
                    order_status="delivered",
                    subtotal=milk_product.price * 2 + mala_product.price * 1,
                    delivery_fee=150.0,
                    total_amount=milk_product.price * 2 + mala_product.price * 1 + 150.0,
                    created_at=order_date.isoformat(),
                    updated_at=order_date.isoformat(),
                )
                db.add(order)
                db.flush()
                item1 = OrderItem(
                    id=str(uuid.uuid4()),
                    order_id=order.id,
                    product_id=milk_product.id,
                    product_name=milk_product.name,
                    quantity=2,
                    unit_price=milk_product.price,
                    total_price=milk_product.price * 2,
                )
                item2 = OrderItem(
                    id=str(uuid.uuid4()),
                    order_id=order.id,
                    product_id=mala_product.id,
                    product_name=mala_product.name,
                    quantity=1,
                    unit_price=mala_product.price,
                    total_price=mala_product.price,
                )
                db.add(item1)
                db.add(item2)
                payment = Payment(
                    id=str(uuid.uuid4()),
                    order_id=order.id,
                    amount=order.total_amount,
                    payment_method="cash_on_delivery",
                    status="completed",
                    transaction_id=f"txn_{uuid.uuid4().hex[:12]}",
                    created_at=order_date.isoformat(),
                    updated_at=order_date.isoformat(),
                )
                db.add(payment)
            db.commit()
            print("Created sample orders")

        print("Seeding complete!")
    finally:
        db.close()


if __name__ == "__main__":
    seed()