import pytest
from unittest.mock import AsyncMock
from app.services.user_service import UserService
from app.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)
from tests.factories import make_user, make_signup_request, make_update_request


@pytest.mark.asyncio
async def test_create_user_successfully(mock_uow):
    data = make_signup_request()
    mock_uow.users.read_by = AsyncMock(return_value=None)
    mock_uow.users.create = AsyncMock(return_value=make_user())

    user = await UserService.create_user(mock_uow, data)

    assert user.email == data.email
    assert user.hashed_password != data.password


@pytest.mark.asyncio
async def test_create_user_already_exists(mock_uow):
    data = make_signup_request()
    mock_uow.users.read_by = AsyncMock(return_value=make_user())

    with pytest.raises(UserAlreadyExistsException):
        await UserService.create_user(mock_uow, data)


@pytest.mark.asyncio
async def test_get_user_with_id(mock_uow):
    existing_user = make_user()
    mock_uow.users.read_by = AsyncMock(return_value=existing_user)

    user = await UserService.get_user_by_id(mock_uow, 1)

    assert user.id == 1
    assert user.email == existing_user.email


@pytest.mark.asyncio
async def test_no_user_with_id(mock_uow):
    mock_uow.users.read_by = AsyncMock(return_value=None)

    with pytest.raises(UserNotFoundException):
        await UserService.get_user_by_id(mock_uow, 1)


@pytest.mark.asyncio
async def test_update_user_successfully(mock_uow):
    data = make_update_request()
    existing_user = make_user()
    updated_user = make_user(hashed_password="new_hash")

    mock_uow.users.read_by = AsyncMock(return_value=existing_user)
    mock_uow.users.update_by = AsyncMock(return_value=updated_user)

    user = await UserService.update_user(mock_uow, 1, data)

    assert user.name == data.name
    assert user.email == data.email
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_existed_user(mock_uow):
    mock_uow.users.read_by = AsyncMock(return_value=make_user())
    mock_uow.users.delete_by = AsyncMock(return_value=None)

    result = await UserService.delete_user(mock_uow, 1)
    assert result is None


@pytest.mark.asyncio
async def test_get_list_of_users(mock_uow):
    users_list = [
        make_user(id=1),
        make_user(id=2, name="Alice", nickname="alice123", email="alice@mail.com"),
    ]

    mock_uow.users.read_all = AsyncMock(return_value=users_list)

    result = await UserService.read_all_users(mock_uow)

    assert len(result.users) == 2
    assert result.users[0].id == 1
    assert result.users[1].id == 2


@pytest.mark.asyncio
async def test_no_user_with_email(mock_uow):
    mock_uow.users.read_by = AsyncMock(return_value=None)

    with pytest.raises(UserNotFoundException):
        await UserService.get_user_by_email(mock_uow, "1234qwer@ukr.net")
