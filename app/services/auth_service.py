from typing import Optional
from uuid import UUID

from app.exceptions.user_exceptions import UserNotFoundException
from app.schemas.user_schema import UserDetailResponse, SignUpRequest
from app.unit_of_work.uow import UnitOfWork
from app.services.user_service import UserService
from app.services.refresh_token_service import RefreshTokenService
from app.utils.access_token_util import AccessTokenUtil
from app.utils.password_util import PasswordUtil
from app.schemas.auth_schema import TokenResponse
from app.exceptions.auth_exceptions import (
    InvalidCredentialsException,
    InvalidRefreshTokenWhileGenerating,
    InvalidTokenType,
    AuthError,
)


class AuthService:
    def __init__(
        self,
        access_token_util: AccessTokenUtil,
        refresh_token_service: RefreshTokenService,
        user_service: UserService,
        password_util: PasswordUtil,
    ):
        self.access_token_util = access_token_util
        self.refresh_token_service = refresh_token_service
        self.user_service = user_service
        self.password_util = password_util

    async def login(
        self, uow: UnitOfWork, email: str, password: str
    ) -> TokenResponse | None:
        user: UserDetailResponse = await self.user_service.get_user_by_email(uow, email)
        if not user:
            return None

        if not self.password_util.verify_password(password, user.hashed_password):
            return None

        access_token = self.access_token_util.create_access_token(str(user.id))
        refresh_token = await self.refresh_token_service.create_refresh_token(
            uow, user.id
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.access_token_util.access_expire_minutes * 60,
        )

    async def auth0_login(self, uow: UnitOfWork, auth0_user: dict) -> TokenResponse:
        email = auth0_user.get("email") or auth0_user.get("https://quizapp.com/email")
        auth0_sub = auth0_user.get("sub")

        if not email:
            raise InvalidCredentialsException()

        user: Optional[UserDetailResponse] = await self.user_service.get_user_by_email(
            uow, email
        )

        if not user:
            name = auth0_user.get("name", "")
            nickname = auth0_user.get("nickname", email.split("@")[0])

            user_data = SignUpRequest(
                email=email,
                name=name,
                surname=None,
                nickname=nickname,
                password=auth0_sub,
            )

            await self.user_service.create_user(uow, user_data)
            user = await self.user_service.get_user_by_email(uow, email)

        access_token = self.access_token_util.create_access_token(str(user.id))
        refresh_token = await self.refresh_token_service.create_refresh_token(
            uow, user.id
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.access_token_util.access_expire_minutes * 60,
        )

    async def refresh(self, uow: UnitOfWork, old_refresh_token: str) -> TokenResponse:
        token_obj = await self.refresh_token_service.verify_refresh_token(
            uow, old_refresh_token
        )
        if not token_obj:
            raise InvalidRefreshTokenWhileGenerating()

        new_refresh_token = await self.refresh_token_service.rotate_refresh_token(
            uow, old_refresh_token, token_obj.user_id
        )
        access_token = self.access_token_util.create_access_token(
            str(token_obj.user_id)
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=self.access_token_util.access_expire_minutes * 60,
        )

    async def logout(self, uow: UnitOfWork, refresh_token: str) -> None:
        await self.refresh_token_service.revoke_refresh_token(uow, refresh_token)

    async def me(self, uow: UnitOfWork, access_token: str) -> UserDetailResponse:
        try:
            payload = self.access_token_util.decode_token(access_token)
            if payload.get("type") != "access":
                raise InvalidTokenType()

            user_id = payload.get("sub")
            user = await self.user_service.get_user_by_id(uow, UUID(user_id))
            if not user:
                raise UserNotFoundException()

            return UserDetailResponse.model_dump(user)

        except Exception as e:
            raise AuthError()

    async def auth0_me(self, uow: UnitOfWork, auth0_user: dict) -> UserDetailResponse:
        email = auth0_user.get("email")

        if not email:
            raise InvalidCredentialsException()

        user = await self.user_service.get_user_by_email(uow, email)
        if not user:
            raise UserNotFoundException()

        return UserDetailResponse.model_dump(user)
