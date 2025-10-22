from fastapi import APIRouter, Depends, status
from uuid import UUID

from app.dependencies.auth_dependency import get_auth_user_from_token

from app.dependencies.uow_dependency import get_uow
from app.schemas.user_schema import (
    SignUpRequest,
    UserDetailResponse,
    UserUpdateRequest,
    UsersListResponse,
)

from app.unit_of_work.uow import UnitOfWork
from app.services.user_service import UserService

user_service = UserService()
router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    data: SignUpRequest, uow: UnitOfWork = Depends(get_uow)
) -> UserDetailResponse:
    return await user_service.create_user(uow, data)


@router.get(
    "/{user_id}", response_model=UserDetailResponse, status_code=status.HTTP_200_OK
)
async def get_user_by_id(
    user_id: UUID, uow: UnitOfWork = Depends(get_uow)
) -> UserDetailResponse:
    return await user_service.get_user_by_id(uow, user_id)


@router.get("/", response_model=UsersListResponse, status_code=status.HTTP_200_OK)
async def read_all_users(
    offset: int = 0, limit: int = 20, uow: UnitOfWork = Depends(get_uow)
) -> UsersListResponse:
    return await user_service.read_all_users(uow, offset, limit)


@router.put(
    "/{user_id}", response_model=UserDetailResponse, status_code=status.HTTP_200_OK
)
async def update_user(
    user_id: UUID,
    data: UserUpdateRequest,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> UserDetailResponse:
    return await user_service.update_user(uow, user_id, data, current_user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> None:
    await user_service.delete_user(uow, user_id, current_user_id)
