import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def client():
    settings = Settings(_env_file=None, app_name="Test Learning Lab", environment="test")
    with TestClient(create_app(settings)) as test_client:
        yield test_client
