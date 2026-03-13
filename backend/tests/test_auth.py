import pytest


def test_register_validation_short_password(client):
    r = client.post(
        "/auth/register",
        json={
            "email": "u@example.com",
            "password": "short",
            "first_name": "A",
            "last_name": "B",
        },
    )
    assert r.status_code == 422  # validation error


def test_register_validation_invalid_email(client):
    r = client.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "password": "longenoughpassword",
            "first_name": "A",
            "last_name": "B",
        },
    )
    assert r.status_code == 422


def test_login_validation(client):
    r = client.post("/auth/login", json={"email": "u@example.com", "password": ""})
    assert r.status_code == 422
