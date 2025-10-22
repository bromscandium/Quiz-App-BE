from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.user_schema import UserDetailResponse
from app.schemas.auth_schema import LoginRequest, TokenResponse, TokenRequest
from app.unit_of_work.uow import UnitOfWork
from app.dependencies.auth0_dependency import get_auth0_user_from_token
from app.dependencies.uow_dependency import get_uow
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

auth_service = AuthService()


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    data: LoginRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> TokenResponse:
    return await auth_service.login(uow, data.email, data.password)


@router.post(
    "/auth0/login", response_model=TokenResponse, status_code=status.HTTP_200_OK
)
async def oauth_login(
    uow: UnitOfWork = Depends(get_uow),
    auth0_user: dict = Depends(get_auth0_user_from_token),
) -> TokenResponse:
    return await auth_service.auth0_login(uow, auth0_user)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh(
    data: TokenRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> TokenResponse:
    return await auth_service.refresh(uow, data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: TokenRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    await auth_service.logout(uow, data.refresh_token)


@router.get("/me", response_model=UserDetailResponse, status_code=status.HTTP_200_OK)
async def me(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    uow: UnitOfWork = Depends(get_uow),
) -> UserDetailResponse:
    access_token = credentials.credentials
    return await auth_service.me(uow, access_token)
