def test_admin_dashboard_access(client, admin_token):
    resp = client.get("/admin", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200


def test_admin_stats_api(client, admin_token):
    resp = client.get("/api/v1/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "today_sales" in data
    assert "pending_orders" in data


def test_admin_products_api(client, admin_token):
    resp = client.get("/api/v1/products", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200


def test_admin_access_denied_without_token(client):
    resp = client.get("/admin")
    assert resp.status_code in (302, 401)


def test_admin_cows_api(client, admin_token):
    resp = client.get("/api/v1/cows", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200


def test_admin_milk_api(client, admin_token):
    resp = client.get("/api/v1/milk", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200