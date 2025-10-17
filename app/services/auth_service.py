from uuid import UUID
import httpx

from app.exceptions.auth_exceptions import (
    InvalidCredentialsException,
    InvalidRefreshTokenWhileGenerating,
    InvalidTokenType,
    AuthError,
    Auth0UserFetchFailed,
    InvalidTokenFormat,
)
from app.exceptions.user_exceptions import UserNotFoundException
from app.schemas.auth_schema import TokenResponse
from app.schemas.user_schema import UserDetailResponse, SignUpRequest
from app.unit_of_work.uow import UnitOfWork
from app.services.user_service import UserService
from app.services.refresh_token_service import RefreshTokenService
from app.utils.access_token_util import AccessTokenUtil
from app.utils.password_util import PasswordUtil
from app.core.security import security_settings
from app.utils.refresh_token_util import RefreshTokenUtil


class AuthService:
    access_token_util: AccessTokenUtil = AccessTokenUtil()
    refresh_token_util: RefreshTokenUtil = RefreshTokenUtil()
    refresh_token_service: RefreshTokenService = RefreshTokenService()
    user_service: UserService = UserService()
    password_util: PasswordUtil = PasswordUtil()

    @classmethod
    async def fetch_auth0_userinfo(cls, token: str) -> dict:
        if not token or len(token.split(".")) != 3:
            raise InvalidTokenFormat

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://{security_settings.auth0.domain}/userinfo",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0,
            )
        if resp.status_code != 200:
            raise Auth0UserFetchFailed

        return resp.json()

    @classmethod
    async def login(
        cls, uow: UnitOfWork, email: str, password: str
    ) -> TokenResponse | None:
        user: UserDetailResponse = await cls.user_service.get_user_by_email(uow, email)
        if not user:
            return None

        if not cls.password_util.verify_password(password, user.hashed_password):
            return None

        access_token = cls.access_token_util.create_access_token(str(user.id))
        refresh_token = await cls.refresh_token_service.create_refresh_token(
            uow, user.id
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=cls.access_token_util.access_expire_minutes * 60,
        )

    @classmethod
    async def auth0_login(cls, uow: UnitOfWork, auth0_user: dict) -> TokenResponse:
        email = auth0_user.get("email") or auth0_user.get("https://quizapp.com/email")
        auth0_sub = auth0_user.get("sub")
        if not email:
            raise InvalidCredentialsException

        user: UserDetailResponse | None = await cls.user_service.get_user_by_email(
            uow, email
        )
        if not user:
            user_data = SignUpRequest(
                email=email,
                name=auth0_user.get("name", ""),
                surname=None,
                nickname=auth0_user.get("nickname", email.split("@")[0]),
                password=auth0_sub,
            )
            await cls.user_service.create_user(uow, user_data)
            user = await cls.user_service.get_user_by_email(uow, email)

        access_token = cls.access_token_util.create_access_token(str(user.id))
        refresh_token = await cls.refresh_token_service.create_refresh_token(
            uow, user.id
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=cls.access_token_util.access_expire_minutes * 60,
        )

    @classmethod
    async def refresh(cls, uow: UnitOfWork, old_refresh_token: str) -> TokenResponse:
        token_obj = await cls.refresh_token_service.verify_refresh_token(
            uow, old_refresh_token
        )
        if not token_obj:
            raise InvalidRefreshTokenWhileGenerating

        new_refresh_token = await cls.refresh_token_service.rotate_refresh_token(
            uow, old_refresh_token, token_obj.user_id
        )
        access_token = cls.access_token_util.create_access_token(str(token_obj.user_id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=cls.access_token_util.access_expire_minutes * 60,
        )

    @classmethod
    async def logout(cls, uow: UnitOfWork, refresh_token: str) -> None:
        await cls.refresh_token_service.revoke_refresh_token(uow, refresh_token)

    @classmethod
    async def me(cls, uow: UnitOfWork, access_token: str) -> UserDetailResponse:
        payload = cls.access_token_util.decode_token(access_token)
        if payload.get("type") != "access":
            raise InvalidTokenType

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenType

        user = await cls.user_service.get_user_by_id(uow, UUID(user_id))
        if not user:
            raise UserNotFoundException

        return UserDetailResponse.model_validate(user)
