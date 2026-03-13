def test_contact_validation_empty_name(client):
    r = client.post(
        "/contact",
        json={
            "name": "",
            "email": "a@b.com",
            "subject": "S",
            "message": "Hello",
        },
    )
    assert r.status_code == 422


def test_contact_validation_invalid_email(client):
    r = client.post(
        "/contact",
        json={
            "name": "Test",
            "email": "invalid",
            "subject": "S",
            "message": "Hello",
        },
    )
    assert r.status_code == 422


def test_contact_success(client):
    r = client.post(
        "/contact",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Question",
            "message": "Hello, I have a question.",
        },
    )
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
