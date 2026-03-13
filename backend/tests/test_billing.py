def test_create_checkout_requires_auth(client):
    r = client.post(
        "/billing/create-checkout-session",
        json={
            "organization_id": 1,
            "success_url": "https://app.example.com/success",
            "cancel_url": "https://app.example.com/cancel",
        },
    )
    assert r.status_code == 401
