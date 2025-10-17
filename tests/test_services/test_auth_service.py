from datetime import timedelta

import pytest
from uuid import uuid4
from app.services.auth_service import AuthService
from app.schemas.user_schema import SignUpRequest
from app.exceptions.auth_exceptions import (
    InvalidRefreshTokenWhileGenerating,
    InvalidTokenType,
)
from app.exceptions.user_exceptions import (
    UserNotFoundException,
    UserInternalErrorException,
)
from app.utils.access_token_util import AccessTokenUtil


@pytest.mark.asyncio
class TestAuthService:
    async def test_login_success(self, uow):
        user_data = SignUpRequest(
            name="John",
            surname="Doe",
            nickname="johndoe",
            email="john.doe@example.com",
            password="SecurePass123!",
        )
        await AuthService.user_service.create_user(uow, user_data)

        token_response = await AuthService.login(
            uow, "john.doe@example.com", "SecurePass123!"
        )
        assert token_response.access_token
        assert token_response.refresh_token
        assert token_response.token_type == "bearer"

    async def test_login_invalid_password(self, uow):
        token_response = await AuthService.login(
            uow, "john.doe@example.com", "WrongPass"
        )
        assert token_response is None

    async def test_login_user_not_found(self, uow):
        token_response = await AuthService.login(uow, "notfound@example.com", "AnyPass")
        assert token_response is None

    async def test_me_success(self, uow):
        user_data = SignUpRequest(
            name="Jane",
            surname="Smith",
            nickname="janesmith",
            email="jane.smith@example.com",
            password="AnotherPass456!",
        )
        user = await AuthService.user_service.create_user(uow, user_data)

        login_response = await AuthService.login(
            uow, "jane.smith@example.com", "AnotherPass456!"
        )
        me_user = await AuthService.me(uow, login_response.access_token)

        assert me_user.id == user.id
        assert me_user.email == user.email

    async def test_me_invalid_token_type(self, uow):
        from pytest import raises

        token_util = AccessTokenUtil()
        token = token_util._create_token(str(uuid4()), delta=timedelta(minutes=1))
        with raises(UserInternalErrorException):
            await AuthService.me(uow, token)

    async def test_me_user_not_found(self, uow):
        from pytest import raises

        token_util = AccessTokenUtil()
        token = token_util._create_token(str(uuid4()), delta=timedelta(seconds=10))
        with raises(UserInternalErrorException):
            await AuthService.me(uow, token)

    async def test_refresh_success(self, uow):
        user_data = SignUpRequest(
            name="Jake",
            surname="Peralta",
            nickname="jakeperalta",
            email="jake@example.com",
            password="N1neNine!",
        )
        await AuthService.user_service.create_user(uow, user_data)
        login_resp = await AuthService.login(uow, "jake@example.com", "N1neNine!")
        old_refresh_token = login_resp.refresh_token

        refreshed = await AuthService.refresh(uow, old_refresh_token)
        assert refreshed.access_token
        assert refreshed.refresh_token
        assert refreshed.refresh_token != old_refresh_token

    async def test_refresh_invalid_token(self, uow):
        from pytest import raises

        with raises(InvalidRefreshTokenWhileGenerating):
            await AuthService.refresh(uow, "invalid_refresh_token")
