from uuid import uuid4

import pytest

from app.exceptions.auth import InvalidRefreshToken, InvalidTokenFormat
from app.exceptions.user import UserNotFound
from app.schemas.user import UserCreate
from app.services.auth import AuthService

auth_service = AuthService()


@pytest.mark.asyncio
class TestAuthService:
    async def test_login_success(self, uow):
        user_data = UserCreate(
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
        user_data = UserCreate(
            name="Jane",
            surname="Smith",
            nickname="janesmith",
            email="jane.smith@example.com",
            password="AnotherPass456!",
        )
        user = await auth_service.user_service.create_user(uow, user_data)

        me_user = await auth_service.me(uow, user.id)

        assert me_user.id == user.id
        assert me_user.email == user.email

    async def test_me_user_not_found(self, uow):
        from pytest import raises

        with raises(UserNotFound):
            await auth_service.me(uow, uuid4())

    async def test_refresh_invalid_token(self, uow):
        from pytest import raises

        with raises(InvalidRefreshToken):
            await auth_service.refresh("invalid_refresh_token")

    async def test_fetch_auth_userinfo_success(self, uow):
        user_data = UserCreate(
            name="Amy",
            surname="Santiago",
            nickname="amysantiago",
            email="amy@example.com",
            password="BinderPass123!",
        )
        user = await auth_service.user_service.create_user(uow, user_data)

        tokens = auth_service.auth_token.create_tokens(str(user.id))
        access_token = tokens["access_token"]

        user_id = await auth_service.fetch_auth_userinfo(access_token)
        assert user_id == user.id

    async def test_fetch_auth_userinfo_invalid_format(self, uow):
        from pytest import raises

        with raises(InvalidTokenFormat):
            await auth_service.fetch_auth_userinfo("invalid_token")

    async def test_logout(self, uow):
        user_data = UserCreate(
            name="Terry",
            surname="Jeffords",
            nickname="terryjeffords",
            email="terry@example.com",
            password="YogurtLove99!",
        )
        user = await auth_service.user_service.create_user(uow, user_data)

        tokens = auth_service.auth_token.create_tokens(str(user.id))
        access_token = tokens["access_token"]

        await auth_service.logout(access_token)
