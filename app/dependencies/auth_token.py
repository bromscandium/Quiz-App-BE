from uuid import UUID

from fastapi import Depends, Cookie

from app.services import AuthService


async def get_auth_user_from_cookie(
        access_token: str | None = Cookie(None, alias="ACCESS_TOKEN"),
        auth_service: AuthService = Depends(),
) -> UUID:
    return await auth_service.fetch_auth_userinfo(access_token)
