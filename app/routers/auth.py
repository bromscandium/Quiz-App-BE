from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.dependencies import *
from app.schemas.auth import LoginRequest, TokenRequest, TokenResponse
from app.schemas.user import UserSchema
from app.services import AuthService
from app.unit_of_work import UnitOfWork

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
) -> TokenResponse:
    return await auth_service.refresh(data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: TokenRequest,
) -> None:
    await auth_service.logout(data.refresh_token)


@router.get("/me", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def me(
    user_id: UUID = Depends(get_auth_user_from_cookie),
    uow: UnitOfWork = Depends(get_uow),
) -> UserSchema:
    return await auth_service.me(uow, user_id)
