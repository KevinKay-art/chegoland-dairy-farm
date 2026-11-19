from app.models.product import Product


def test_create_order(client, admin_token, db):
    product = Product(
        id="order-product-id",
        name="Order Product",
        slug="order-product",
        description="For order",
        category="milk",
        price=100.0,
        unit="litre",
        stock_quantity=10,
    )
    db.add(product)
    db.commit()

    client.post("/api/v1/cart/add", json={"product_id": "order-product-id", "quantity": 2})

    resp = client.post("/api/v1/orders", json={
        "customer_name": "Test Customer",
        "customer_phone": "+254700000000",
        "customer_email": "test@test.com",
        "delivery_address": "Test Address",
        "delivery_date": "2026-12-01",
        "delivery_time_slot": "Morning (8am-12pm)",
        "payment_method": "cash_on_delivery",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "order_id" in data
    assert "order_number" in data


def test_create_order_insufficient_stock(client, db):
    product = Product(
        id="low-stock-product",
        name="Low Stock",
        slug="low-stock",
        description="Low",
        category="milk",
        price=100.0,
        unit="litre",
        stock_quantity=1,
    )
    db.add(product)
    db.commit()

    client.post("/api/v1/cart/add", json={"product_id": "low-stock-product", "quantity": 5})
    resp = client.post("/api/v1/orders", json={
        "customer_name": "Test",
        "customer_phone": "+254700000000",
        "delivery_address": "Test",
        "payment_method": "cash_on_delivery",
    })
    assert resp.status_code == 400


def test_list_orders(client, admin_token, db):
    resp = client.get("/api/v1/orders", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200


def test_get_order(client, admin_token, db):
    from app.models.order import Order
    order = Order(
        id="test-order-id",
        order_number="CG20260101TEST",
        user_id=None,
        customer_name="Test",
        customer_phone="+254700000000",
        delivery_address="Test",
        payment_method="cash_on_delivery",
        payment_status="pending",
        order_status="pending",
        subtotal=100.0,
        delivery_fee=150.0,
        total_amount=250.0,
    )
    db.add(order)
    db.commit()

    resp = client.get("/api/v1/orders/test-order-id", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["order_number"] == "CG20260101TEST"