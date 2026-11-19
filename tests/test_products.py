from app.models.product import Product


def test_list_products(client):
    resp = client.get("/api/v1/products")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_create_product(client, admin_token, db):
    resp = client.post("/api/v1/products", headers={"Authorization": f"Bearer {admin_token}"}, data={
        "name": "Test Milk",
        "slug": "test-milk",
        "description": "Test description",
        "category": "milk",
        "price": 100.0,
        "unit": "litre",
        "stock_quantity": 50,
        "is_active": "true",
        "is_featured": "false",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Milk"

    product = db.query(Product).filter(Product.slug == "test-milk").first()
    assert product is not None
    assert product.price == 100.0


def test_create_product_unauthorized(client):
    resp = client.post("/api/v1/products", data={
        "name": "Test",
        "slug": "test",
        "category": "milk",
        "price": 10.0,
        "unit": "litre",
        "stock_quantity": 0,
    })
    assert resp.status_code == 401


def test_get_product(client, admin_token, db):
    product = Product(
        id="test-product-id",
        name="Direct Product",
        slug="direct-product",
        description="Direct",
        category="milk",
        price=50.0,
        unit="litre",
        stock_quantity=10,
    )
    db.add(product)
    db.commit()

    resp = client.get("/api/v1/products/test-product-id")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Direct Product"