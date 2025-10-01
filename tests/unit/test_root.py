import os

os.environ["QUIZAPP_HOST"] = "127.0.0.1"
os.environ["QUIZAPP_PORT"] = "8000"
os.environ["QUIZAPP_CORS_ORIGINS"] = "*"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status_code": 200, "detail": "ok", "result": "working"}
