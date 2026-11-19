def test_mpesa_stk_push_mock(client, admin_token, db):
    from app.models.order import Order
    order = Order(
        id="mpesa-order-id",
        order_number="CG2026MPESA",
        user_id=None,
        customer_name="MPesa User",
        customer_phone="+254700000000",
        delivery_address="Test",
        payment_method="mpesa",
        payment_status="pending",
        order_status="pending",
        subtotal=100.0,
        delivery_fee=150.0,
        total_amount=250.0,
    )
    db.add(order)
    db.commit()

    resp = client.post("/api/v1/payments/mpesa/stk-push", json={
        "phone_number": "+254700000000",
        "amount": 250.0,
        "order_id": "mpesa-order-id",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "checkout_request_id" in data


def test_mpesa_callback_success(client, admin_token, db):
    from app.models.order import Order
    from app.models.payment import Payment
    order = Order(
        id="callback-order-id",
        order_number="CG2026CALLBACK",
        user_id=None,
        customer_name="Callback User",
        customer_phone="+254700000000",
        delivery_address="Test",
        payment_method="mpesa",
        payment_status="pending",
        order_status="pending",
        subtotal=100.0,
        delivery_fee=150.0,
        total_amount=250.0,
    )
    db.add(order)
    db.flush()
    payment = Payment(
        id="callback-payment-id",
        order_id="callback-order-id",
        amount=250.0,
        payment_method="mpesa",
        status="pending",
        checkout_request_id="ws_CO_test123",
        created_at="2026-01-01T00:00:00",
        updated_at="2026-01-01T00:00:00",
    )
    db.add(payment)
    db.commit()

    resp = client.post("/api/v1/payments/mpesa/callback", json={
        "Body": {
            "stkCallback": {
                "CheckoutRequestID": "ws_CO_test123",
                "ResultCode": "0",
                "ResultDesc": "Success",
                "CallbackMetadata": {
                    "Item": [
                        {"Name": "Amount", "Value": 250.0},
                        {"Name": "MpesaReceiptNumber", "Value": "RECEIPT123"},
                        {"Name": "PhoneNumber", "Value": "254700000000"},
                    ]
                },
            }
        }
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"