from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services import AuthService


async def get_auth_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    auth_service: AuthService = Depends(),
) -> UUID:
    return await auth_service.fetch_auth_userinfo(credentials.credentials)
