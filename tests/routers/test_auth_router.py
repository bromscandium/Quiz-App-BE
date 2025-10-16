from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from tests.factories import make_user


@pytest.mark.asyncio
async def test_login_success(client, mock_uow):
    user = make_user()
    login_data = {"email": user.email, "password": "correct_password"}

    with patch(
        "app.services.auth_service.AuthService.login", new_callable=AsyncMock
    ) as mock_login:
        mock_login.return_value = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_123",
            "token_type": "bearer",
            "expires_in": 3600,
        }
        response = await client.post("/auth/login", json=login_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client, mock_uow):
    from app.exceptions.auth_exceptions import InvalidCredentialsException

    login_data = {"email": "wrong@example.com", "password": "wrong_password"}

    with patch(
        "app.services.auth_service.AuthService.login", new_callable=AsyncMock
    ) as mock_login:
        mock_login.side_effect = InvalidCredentialsException()
        response = await client.post("/auth/login", json=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_success(client, mock_uow):
    refresh_data = {"refresh_token": "valid_refresh_token"}

    with patch(
        "app.services.auth_service.AuthService.refresh", new_callable=AsyncMock
    ) as mock_refresh:
        mock_refresh.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "token_type": "bearer",
            "expires_in": 3600,
        }
        response = await client.post("/auth/refresh", json=refresh_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_logout_success(client, mock_uow):
    logout_data = {"refresh_token": "valid_refresh_token"}

    with patch(
        "app.services.auth_service.AuthService.logout", new_callable=AsyncMock
    ) as mock_logout:
        mock_logout.return_value = None
        response = await client.post("/auth/logout", json=logout_data)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_logout_token_not_found(client, mock_uow):
    from app.exceptions.refresh_token_exceptions import NotFoundRefreshToken

    logout_data = {"refresh_token": "nonexistent_token"}

    with patch(
        "app.services.auth_service.AuthService.logout", new_callable=AsyncMock
    ) as mock_logout:
        mock_logout.side_effect = NotFoundRefreshToken()
        response = await client.post("/auth/logout", json=logout_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
