from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services import AuthService


async def get_auth0_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    auth_service: AuthService = Depends(),
) -> dict:
    return await auth_service.fetch_auth0_userinfo(credentials.credentials)
