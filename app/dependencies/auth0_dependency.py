from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth_service import AuthService

auth_service = AuthService()


async def get_auth0_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> dict:
    return await auth_service.fetch_auth0_userinfo(credentials.credentials)
