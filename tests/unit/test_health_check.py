import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status_code"] == 200
    assert data["detail"] == "ok"
    assert data["result"] == "working"


def test_health_check_db():
    response = client.get("/db")
    if response.status_code == 503:
        pytest.skip("Database not available for testing")

    assert response.status_code == 200
    data = response.json()
    assert data["database"] == "ok"


def test_health_check_redis():
    response = client.get("/redis")
    if response.status_code == 503:
        pytest.skip("Redis not available for testing")

    assert response.status_code == 200
    data = response.json()
    assert data["redis"] == "ok"
