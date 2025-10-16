import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.services.user_service import UserService
from app.services.refresh_token_service import RefreshTokenService
from app.utils.refresh_token_util import RefreshTokenUtil
from app.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)
from tests.factories import make_user, make_signup_request, make_update_request


@pytest.fixture
def user_service():
    refresh_token_util = RefreshTokenUtil()
    refresh_token_service = RefreshTokenService(refresh_token_util)
    return UserService(refresh_token_service)


@pytest.mark.asyncio
async def test_create_user_successfully(mock_uow, user_service):
    data = make_signup_request()
    created_user = make_user()
    mock_uow.users.read_by = AsyncMock(return_value=None)
    mock_uow.users.create = AsyncMock(return_value=created_user)

    user = await user_service.create_user(mock_uow, data)

    assert user.email == data.email
    assert user.hashed_password != data.password


@pytest.mark.asyncio
async def test_create_user_already_exists(mock_uow, user_service):
    data = make_signup_request()
    mock_uow.users.read_by = AsyncMock(return_value=make_user())

    with pytest.raises(UserAlreadyExistsException):
        await user_service.create_user(mock_uow, data)


@pytest.mark.asyncio
async def test_get_user_with_id(mock_uow, user_service):
    existing_user = make_user()
    mock_uow.users.read_by = AsyncMock(return_value=existing_user)

    user = await user_service.get_user_by_id(mock_uow, existing_user.id)

    assert user.id == existing_user.id
    assert user.email == existing_user.email


@pytest.mark.asyncio
async def test_no_user_with_id(mock_uow, user_service):
    user_id = uuid4()
    mock_uow.users.read_by = AsyncMock(return_value=None)

    with pytest.raises(UserNotFoundException):
        await user_service.get_user_by_id(mock_uow, user_id)


@pytest.mark.asyncio
async def test_update_user_successfully(mock_uow, user_service):
    data = make_update_request()
    existing_user = make_user()
    updated_user = make_user(hashed_password="new_hash")

    mock_uow.users.read_by = AsyncMock(return_value=existing_user)
    mock_uow.users.update_by = AsyncMock(return_value=updated_user)

    user = await user_service.update_user(mock_uow, existing_user.id, data)

    assert user.name == data.name
    assert user.email == data.email
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_existed_user(mock_uow, user_service):
    existing_user = make_user()
    mock_uow.users.read_by = AsyncMock(return_value=existing_user)
    mock_uow.users.delete_by = AsyncMock(return_value=None)

    with patch.object(
        user_service.refresh_token, "delete_refresh_token", new_callable=AsyncMock
    ):
        result = await user_service.delete_user(mock_uow, existing_user.id)

    assert result is None


@pytest.mark.asyncio
async def test_get_list_of_users(mock_uow, user_service):
    user1 = make_user()
    user2 = make_user(name="Alice", nickname="alice123", email="alice@mail.com")
    users_list = [user1, user2]

    mock_uow.users.read_all = AsyncMock(return_value=users_list)

    result = await user_service.read_all_users(mock_uow)

    assert len(result.users) == 2
    assert result.users[0].id == user1.id
    assert result.users[1].id == user2.id


@pytest.mark.asyncio
async def test_no_user_with_email(mock_uow, user_service):
    mock_uow.users.read_by = AsyncMock(return_value=None)

    user = await user_service.get_user_by_email(mock_uow, "1234qwer@ukr.net")
    assert user is None
