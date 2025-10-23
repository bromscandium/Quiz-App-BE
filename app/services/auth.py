from uuid import UUID
import httpx

from app.exceptions.auth import (
    InvalidCredentialsException,
    InvalidRefreshTokenWhileGenerating,
    InvalidTokenType,
    Auth0UserFetchFailed,
    InvalidTokenFormat,
    AuthUserFetchFailed,
)
from app.exceptions.refresh_token import NotFoundRefreshToken
from app.exceptions.user import UserNotFoundException
from app.schemas.auth import TokenResponse
from app.schemas.user import UserDetailResponse, UserCreateRequest
from app.unit_of_work.uow import UnitOfWork
from app.services.user import UserService
from app.utils import logger
from app.utils.access_token import AccessTokenUtil
from app.utils.password import PasswordUtil
from app.core.security import security_settings
from app.utils.refresh_token import RefreshTokenUtil


class AuthService:
    def __init__(self):
        self.access_token_util = AccessTokenUtil()
        self.refresh_token_util = RefreshTokenUtil()
        self.user_service = UserService()
        self.password_util = PasswordUtil()

    async def fetch_auth0_userinfo(self, token: str) -> dict:
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

    async def fetch_auth_userinfo(self, token: str) -> UUID:
        if not token or len(token.split(".")) != 3:
            raise InvalidTokenFormat

        try:
            payload = self.access_token_util.decode_token(token)
            user_id: UUID = payload.get("sub")

            if user_id is None:
                raise UserNotFoundException
        except:
            raise AuthUserFetchFailed

        return UUID(user_id)

    async def login(
        self, uow: UnitOfWork, email: str, password: str
    ) -> TokenResponse | None:
        user: UserDetailResponse = await self.user_service.get_user_by_email(uow, email)
        if not user:
            return None

        if not self.password_util.verify_password(password, user.hashed_password):
            return None

        access_token = self.access_token_util.create_access_token(str(user.id))
        refresh_token = await self.refresh_token_util.create_refresh_token(uow, user.id)

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
            raise InvalidCredentialsException

        user: UserDetailResponse | None = await self.user_service.get_user_by_email(
            uow, email
        )
        if not user:
            user_data = UserCreateRequest(
                email=email,
                name=auth0_user.get("name", ""),
                surname=None,
                nickname=auth0_user.get("nickname", email.split("@")[0]),
                password=auth0_sub,
            )
            await self.user_service.create_user(uow, user_data)
            user = await self.user_service.get_user_by_email(uow, email)

        access_token = self.access_token_util.create_access_token(str(user.id))
        refresh_token = await self.refresh_token_util.create_refresh_token(uow, user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.access_token_util.access_expire_minutes * 60,
        )

    async def refresh(self, uow: UnitOfWork, old_refresh_token: str) -> TokenResponse:
        token_obj = await self.refresh_token_util.verify_refresh_token(
            uow, old_refresh_token
        )
        if not token_obj:
            raise InvalidRefreshTokenWhileGenerating

        new_refresh_token = await self.refresh_token_util.rotate_refresh_token(
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

    async def logout(self, uow: UnitOfWork, raw_token: str) -> None:
        try:
            token_obj = await self.refresh_token_util.verify_refresh_token(
                uow, raw_token
            )
            if not token_obj:
                raise NotFoundRefreshToken
            await uow.refresh_tokens.update_by("id", token_obj.id, revoked=True)
        except NotFoundRefreshToken:
            raise
        except Exception as e:
            logger.exception(f"Error revoking refresh token: {e}")
            raise

    async def me(self, uow: UnitOfWork, access_token: str) -> UserDetailResponse:
        payload = self.access_token_util.decode_token(access_token)
        if payload.get("type") != "access":
            raise InvalidTokenType

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenType

        user = await self.user_service.get_user_by_id(uow, UUID(user_id))
        if not user:
            raise UserNotFoundException

        return UserDetailResponse.model_validate(user)
