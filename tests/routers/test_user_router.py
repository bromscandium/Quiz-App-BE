import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status
from uuid import uuid4

from app.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)
from tests.factories import (
    make_user,
    make_signup_request,
    make_user_detail_response,
)
from app.schemas.user_schema import UsersListResponse, UserSchema


@pytest.mark.asyncio
async def test_create_user_success(client, mock_uow):
    data = make_signup_request()
    created_user = make_user()

    with patch(
        "app.services.user_service.UserService.create_user", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = created_user
        response = await client.post("/users/", json=data.model_dump())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == data.email
    assert response.json()["name"] == data.name
    assert "password" not in response.json()


@pytest.mark.asyncio
async def test_create_user_already_exists(client, mock_uow):
    data = make_signup_request()

    with patch(
        "app.services.user_service.UserService.create_user", new_callable=AsyncMock
    ) as mock_create:
        mock_create.side_effect = UserAlreadyExistsException()
        response = await client.post("/users/", json=data.model_dump())

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "User already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_by_id_success(client, mock_uow):
    expected_user = make_user_detail_response()

    with patch(
        "app.services.user_service.UserService.get_user_by_id", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = expected_user
        response = await client.get(f"/users/{expected_user.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == str(expected_user.id)
    assert response.json()["email"] == expected_user.email


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(client, mock_uow):
    user_id = uuid4()

    with patch(
        "app.services.user_service.UserService.get_user_by_id", new_callable=AsyncMock
    ) as mock_get:
        mock_get.side_effect = UserNotFoundException()
        response = await client.get(f"/users/{user_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_read_all_users_success(client, mock_uow):
    user1 = make_user()
    user2 = make_user(name="Alice", nickname="alice123", email="alice@mail.com")
    users_list = [user1, user2]

    with patch(
        "app.services.user_service.UserService.read_all_users", new_callable=AsyncMock
    ) as mock_list:
        mock_list.return_value = UsersListResponse(
            users=[UserSchema.model_validate(u) for u in users_list]
        )
        response = await client.get("/users/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["users"]) == 2


@pytest.mark.asyncio
async def test_delete_user_success(client, mock_uow):
    user_id = uuid4()

    with patch(
        "app.services.user_service.UserService.delete_user", new_callable=AsyncMock
    ) as mock_delete:
        mock_delete.return_value = None
        response = await client.delete(f"/users/{user_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_user_not_found(client, mock_uow):
    user_id = uuid4()

    with patch(
        "app.services.user_service.UserService.delete_user", new_callable=AsyncMock
    ) as mock_delete:
        mock_delete.side_effect = UserNotFoundException()
        response = await client.delete(f"/users/{user_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User not found"
