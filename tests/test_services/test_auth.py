from tests.fixtures import *


@pytest.mark.asyncio
async def test_login_success(uow, user_service, auth_service, user_1_create):
    user = await user_service.create_user(uow=uow, data=user_1_create)

    password = "12345678"
    token_response = await auth_service.login(uow, user.email, password)
    assert token_response is not None
    assert token_response.access_token
    assert token_response.refresh_token


@pytest.mark.asyncio
async def test_login_invalid_password(uow, user_service, auth_service, user_1_create):
    user = await user_service.create_user(uow, user_1_create)

    with pytest.raises(Exception):
        await auth_service.login(user_service.uow, user.email, "wrongpassword")


@pytest.mark.asyncio
async def test_login_user_not_found(uow, auth_service):
    result = await auth_service.login(uow, "nonexistent@example.com", "password")
    assert result is None


@pytest.mark.asyncio
async def test_me_success(uow, user_service, auth_service, user_1_create):
    user = await user_service.create_user(uow, user_1_create)

    result = await auth_service.me(uow, user.id)
    assert result.id == user.id
    assert result.email == user.email
