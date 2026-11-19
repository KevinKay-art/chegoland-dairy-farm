from app.models.product import Product


def test_add_to_cart(client, db):
    product = Product(
        id="cart-product-id",
        name="Cart Product",
        slug="cart-product",
        description="For cart",
        category="milk",
        price=100.0,
        unit="litre",
        stock_quantity=10,
    )
    db.add(product)
    db.commit()

    resp = client.post("/api/v1/cart/add", json={"product_id": "cart-product-id", "quantity": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["count"] == 2


def test_get_cart(client):
    resp = client.get("/api/v1/cart")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data


def test_update_cart(client, db):
    product = Product(
        id="update-cart-product",
        name="Update Cart",
        slug="update-cart",
        description="Update",
        category="milk",
        price=50.0,
        unit="litre",
        stock_quantity=10,
    )
    db.add(product)
    db.commit()

    client.post("/api/v1/cart/add", json={"product_id": "update-cart-product", "quantity": 1})
    resp = client.post("/api/v1/cart/update", json={"product_id": "update-cart-product", "quantity": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 3


def test_remove_from_cart(client, db):
    product = Product(
        id="remove-cart-product",
        name="Remove Cart",
        slug="remove-cart",
        description="Remove",
        category="milk",
        price=30.0,
        unit="litre",
        stock_quantity=10,
    )
    db.add(product)
    db.commit()

    client.post("/api/v1/cart/add", json={"product_id": "remove-cart-product", "quantity": 1})
    resp = client.post("/api/v1/cart/remove", json={"product_id": "remove-cart-product"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 0