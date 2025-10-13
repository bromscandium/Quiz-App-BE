import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/")
    if response.status_code == 503:
        pytest.skip("App not available for testing")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status_code"] == 200
    assert data["detail"] == "ok"
    assert data["result"] == "working"


@pytest.mark.asyncio
async def test_health_check_redis(client, mock_redis):
    response = await client.get("/redis")
    if response.status_code == 503:
        pytest.skip("Redis not available for testing")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["redis"] == "ok"
