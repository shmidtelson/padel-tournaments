def test_health_liveness(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_health_ready(client):
    r = client.get("/health/ready")
    # Without DB: 503; with DB: 200
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        assert r.json().get("db") == "up"
