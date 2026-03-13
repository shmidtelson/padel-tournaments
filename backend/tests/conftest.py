import os
import warnings

import pytest
from fastapi.testclient import TestClient

# Suppress third-party deprecation (passlib uses crypt removed in Python 3.13)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="passlib")

# Ensure we don't run production validation in tests
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-at-least-32-characters-long")

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)
