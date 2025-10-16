import httpx
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import security_settings
from app.utils.auth0_util import Auth0TokenUtil
from app.exceptions.auth_exceptions import InvalidTokenFormat, Auth0UserFetchFailed


class Auth0Dependency:
    def __init__(self):
        self.security = HTTPBearer()
        self.auth0_util = Auth0TokenUtil()
        self.auth0_domain = security_settings.auth0.domain

    async def get_current_user(
        self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> dict:
        token = credentials.credentials
        if not token or len(token.split(".")) != 3:
            raise InvalidTokenFormat()

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://{self.auth0_domain}/userinfo",
                headers={"Authorization": f"Bearer {token}"},
            )
            if resp.status_code != 200:
                raise Auth0UserFetchFailed()

            user_info = resp.json()

        return user_info


auth0_dependency = Auth0Dependency()
