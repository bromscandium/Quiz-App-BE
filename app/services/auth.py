from uuid import UUID

import httpx
from starlette import status

from app.core.security import security_settings
from app.exceptions import (
    Auth0Failed,
    AuthFailed,
    InvalidEmail,
    InvalidPassword,
    InvalidTokenFormat,
    UserNotFound,
)
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserSchema
from app.services.user import UserService
from app.unit_of_work import UnitOfWork
from app.utils import AuthTokenUtil, PasswordUtil, LoggerUtil


class AuthService:
    def __init__(self):
        self.auth_token = AuthTokenUtil()
        self.user_service = UserService()
        self.password_util = PasswordUtil()
        self.logger_util = LoggerUtil()

    async def fetch_auth0_userinfo(self, token: str) -> dict:
        if not token or len(token.split(".")) != 3:
            raise InvalidTokenFormat

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://{security_settings.auth0.domain}/userinfo",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0,
            )
        if resp.status_code != status.HTTP_200_OK:
            raise Auth0Failed

        return resp.json()

    async def fetch_auth_userinfo(self, token: str) -> UUID:
        if not token or len(token.split(".")) != 3:
            raise InvalidTokenFormat

        payload = self.auth_token.decode_token(token)
        user_id: UUID = payload.get("sub")

        if user_id is None:
            raise AuthFailed

        return UUID(user_id)

    async def login(
            self, uow: UnitOfWork, email: str, password: str
    ) -> TokenResponse | None:
        user: UserSchema = await self.user_service.read_user_by_email(uow, email)
        if not user:
            raise UserNotFound

        if not self.password_util.verify_password(password, user.hashed_password):
            raise InvalidPassword

        tokens = self.auth_token.create_tokens(str(user.id))

        return TokenResponse(
            access_token=tokens["ACCESS_TOKEN"],
            refresh_token=tokens["REFRESH_TOKEN"],
            token_type="Bearer",
            expires_in=self.auth_token.access_expire_minutes * 60,
        )

    async def auth0_login(self, uow: UnitOfWork, auth0_user: dict) -> TokenResponse:
        email = auth0_user.get("email")
        auth0_sub = auth0_user.get("sub")
        if not email:
            raise InvalidEmail

        user: UserSchema | None = await self.user_service.read_user_by_email(uow, email)
        if not user:
            user_data = UserCreate(
                email=email,
                name=auth0_user.get("name", ""),
                surname=None,
                nickname=auth0_user.get("nickname", email.split("@")[0]),
                password=auth0_sub,
            )
            await self.user_service.create_user(uow, user_data)
            await uow.session.flush()

            user = await self.user_service.read_user_by_email(uow, email)

        tokens = self.auth_token.create_tokens(str(user.id))

        return TokenResponse(
            access_token=tokens["ACCESS_TOKEN"],
            refresh_token=tokens["REFRESH_TOKEN"],
            token_type="bearer",
            expires_in=self.auth_token.access_expire_minutes * 60,
        )

    async def refresh(self, old_refresh_token: str) -> TokenResponse:
        tokens = self.auth_token.refresh_tokens(old_refresh_token)
        if not tokens:
            raise AuthFailed

        return TokenResponse(
            access_token=tokens["ACCESS_TOKEN"],
            refresh_token=tokens["REFRESH_TOKEN"],
            token_type="bearer",
            expires_in=self.auth_token.access_expire_minutes * 60,
        )

    async def logout(self, raw_token: str) -> None:
        decoded_token = self.auth_token.decode_token(raw_token)
        self.logger_util.info(f"User with {decoded_token['sub']} logged out.")


    async def me(self, uow: UnitOfWork, user_id: UUID) -> UserSchema:
        user = await self.user_service.read_user_by_id(uow, user_id)
        if not user:
            raise AuthFailed

        return UserSchema.model_validate(user)
