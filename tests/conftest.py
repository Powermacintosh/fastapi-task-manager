import pytest
from fastapi.testclient import TestClient
from main import app
from core.config import settings


@pytest.fixture(scope='session')
def client():
    assert settings.db.MODE == 'TEST'
    with TestClient(app) as test_client:
        yield test_client
