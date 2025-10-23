from datetime import timedelta

import pytest
from uuid import uuid4
from app.services.auth import AuthService
from app.schemas.user import UserCreateRequest
from app.exceptions.auth import (
    InvalidRefreshTokenWhileGenerating,
)
from app.exceptions.user import (
    UserInternalErrorException,
    UserNotFoundException,
)
from app.utils.access_token import AccessTokenUtil

auth_service = AuthService()


@pytest.mark.asyncio
class TestAuthService:
    async def test_login_success(self, uow):
        user_data = UserCreateRequest(
            name="John",
            surname="Doe",
            nickname="johndoe",
            email="john.doe@example.com",
            password="SecurePass123!",
        )
        await auth_service.user_service.create_user(uow, user_data)

        token_response = await auth_service.login(
            uow, "john.doe@example.com", "SecurePass123!"
        )
        assert token_response.access_token
        assert token_response.refresh_token
        assert token_response.token_type == "bearer"

    async def test_login_invalid_password(self, uow):
        token_response = await auth_service.login(
            uow, "john.doe@example.com", "WrongPass"
        )
        assert token_response is None

    async def test_login_user_not_found(self, uow):
        token_response = await auth_service.login(
            uow, "notfound@example.com", "AnyPass"
        )
        assert token_response is None

    async def test_me_success(self, uow):
        user_data = UserCreateRequest(
            name="Jane",
            surname="Smith",
            nickname="janesmith",
            email="jane.smith@example.com",
            password="AnotherPass456!",
        )
        user = await auth_service.user_service.create_user(uow, user_data)

        login_response = await auth_service.login(
            uow, "jane.smith@example.com", "AnotherPass456!"
        )
        me_user = await auth_service.me(uow, login_response.access_token)

        assert me_user.id == user.id
        assert me_user.email == user.email

    async def test_me_invalid_token_type(self, uow):
        from pytest import raises

        token_util = AccessTokenUtil()
        token = token_util._create_token(str(uuid4()), delta=timedelta(minutes=1))
        with raises(UserNotFoundException):
            await auth_service.me(uow, token)

    async def test_me_user_not_found(self, uow):
        from pytest import raises

        token_util = AccessTokenUtil()
        token = token_util._create_token(str(uuid4()), delta=timedelta(seconds=10))
        with raises(UserNotFoundException):
            await auth_service.me(uow, token)

    async def test_refresh_success(self, uow):
        user_data = UserCreateRequest(
            name="Jake",
            surname="Peralta",
            nickname="jakeperalta",
            email="jake@example.com",
            password="N1neNine!",
        )
        await auth_service.user_service.create_user(uow, user_data)
        login_resp = await auth_service.login(uow, "jake@example.com", "N1neNine!")
        old_refresh_token = login_resp.refresh_token

        refreshed = await auth_service.refresh(uow, old_refresh_token)
        assert refreshed.access_token
        assert refreshed.refresh_token
        assert refreshed.refresh_token != old_refresh_token

    async def test_refresh_invalid_token(self, uow):
        from pytest import raises

        with raises(InvalidRefreshTokenWhileGenerating):
            await auth_service.refresh(uow, "invalid_refresh_token")
