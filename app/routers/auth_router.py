from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.user_schema import UserDetailResponse
from app.services.user_service import UserService
from app.unit_of_work.uow import UnitOfWork
from app.db.postgres import async_session
from app.services.auth_service import AuthService
from app.services.refresh_token_service import RefreshTokenService
from app.utils.access_token_util import AccessTokenUtil
from app.utils.refresh_token_util import RefreshTokenUtil
from app.utils.password_util import PasswordUtil
from app.schemas.auth_schema import LoginRequest, TokenResponse, TokenRequest
from app.dependencies.auth0_dependency import auth0_dependency

router = APIRouter(prefix="/auth", tags=["auth"])


async def get_uow():
    async with UnitOfWork(async_session) as uow:
        yield uow


def get_auth_service() -> AuthService:
    access_util = AccessTokenUtil()
    refresh_service = RefreshTokenService(refresh_token_util=RefreshTokenUtil())
    user_service = UserService(refresh_service)
    password_util = PasswordUtil()
    return AuthService(access_util, refresh_service, user_service, password_util)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    data: LoginRequest,
    uow: UnitOfWork = Depends(get_uow),
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.login(uow, data.email, data.password)


@router.post(
    "/auth0/login", response_model=TokenResponse, status_code=status.HTTP_200_OK
)
async def oauth_login(
    uow: UnitOfWork = Depends(get_uow),
    auth_service: AuthService = Depends(get_auth_service),
    auth0_user: dict = Depends(auth0_dependency.get_current_user),
):
    return await auth_service.auth0_login(uow, auth0_user)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh(
    data: TokenRequest,
    uow: UnitOfWork = Depends(get_uow),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await auth_service.refresh(uow, data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: TokenRequest,
    uow: UnitOfWork = Depends(get_uow),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.logout(uow, data.refresh_token)


@router.get("/me", response_model=UserDetailResponse, status_code=status.HTTP_200_OK)
async def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    uow: UnitOfWork = Depends(get_uow),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserDetailResponse:
    return await auth_service.me(uow, credentials.credentials)


@router.get(
    "/auth0/me", response_model=UserDetailResponse, status_code=status.HTTP_200_OK
)
async def get_auth0_me(
    uow: UnitOfWork = Depends(get_uow),
    auth0_user: dict = Depends(auth0_dependency.get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserDetailResponse:
    return await auth_service.auth0_me(uow, auth0_user)
