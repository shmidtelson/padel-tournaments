import os
import pytest
from fastapi.testclient import TestClient

# Ensure we don't run production validation in tests
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-at-least-32-characters-long")

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)
