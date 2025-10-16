from fastapi import APIRouter, Depends
from uuid import UUID
from app.exceptions.user_exceptions import *
from app.models import User
from app.services.refresh_token_service import RefreshTokenService
from app.unit_of_work.uow import UnitOfWork
from app.db.postgres import async_session
from app.services.user_service import UserService
from app.schemas.user_schema import (
    SignUpRequest,
    UserDetailResponse,
    UserUpdateRequest,
    UsersListResponse,
    UserSchema,
)
from app.utils.refresh_token_util import RefreshTokenUtil

router = APIRouter(prefix="/users", tags=["users"])


async def get_uow():
    async with UnitOfWork(async_session) as uow:
        yield uow


async def get_user_service() -> UserService:
    refresh_token_service = RefreshTokenService(refresh_token_util=RefreshTokenUtil())
    return UserService(refresh_token_service)


@router.post(
    "/",
    response_model=UserDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Creates a new user in the system. Raises 400 if user already exists or validation fails.",
)
async def create_user(
    data: SignUpRequest,
    uow: UnitOfWork = Depends(get_uow),
    user_service: UserService = Depends(get_user_service),
) -> User:
    return await user_service.create_user(uow, data)


@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Fetches a user by their unique ID. Returns 404 if the user does not exist.",
)
async def get_user_by_id(
    user_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
    user_service: UserService = Depends(get_user_service),
) -> UserDetailResponse | None:
    return await user_service.get_user_by_id(uow, user_id)


@router.get(
    "/",
    response_model=UsersListResponse,
    status_code=status.HTTP_200_OK,
    summary="List users",
    description="Returns a paginated list of users. Supports offset and limit for pagination.",
)
async def read_all_users(
    offset: int = 0,
    limit: int = 20,
    uow: UnitOfWork = Depends(get_uow),
    user_service: UserService = Depends(get_user_service),
) -> UsersListResponse:
    return await user_service.read_all_users(uow, offset, limit)


@router.put(
    "/{user_id}",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    summary="Update user",
    description="Updates a user's details by their ID. Returns 404 if the user does not exist.",
)
async def update_user(
    user_id: UUID,
    data: UserUpdateRequest,
    uow: UnitOfWork = Depends(get_uow),
    user_service: UserService = Depends(get_user_service),
) -> UserSchema:
    return await user_service.update_user(uow, user_id, data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Deletes a user by their ID. Returns 404 if the user does not exist.",
)
async def delete_user(
    user_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
    user_service: UserService = Depends(get_user_service),
) -> None:
    await user_service.delete_user(uow, user_id)
