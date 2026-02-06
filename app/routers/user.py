from fastapi import APIRouter, Depends, status
from uuid import UUID

from pydantic import EmailStr

from app.dependencies.auth_token import get_auth_user_from_token

from app.dependencies.uow import get_uow
from app.schemas.user import (
    UserCreate,
    UserSchema,
    UserUpdate,
    UsersList,
    UserOwnedCompaniesList,
)

from app.unit_of_work.uow import UnitOfWork
from app.services.user import UserService

user_service = UserService()
router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate, uow: UnitOfWork = Depends(get_uow)
) -> UserSchema:
    return await user_service.create_user(uow, data)


@router.get("/id/{user_id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def read_user_by_id(
    user_id: UUID, uow: UnitOfWork = Depends(get_uow)
) -> UserSchema | None:
    return await user_service.read_user_by_id(uow, user_id)


@router.get("/email/{email}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def read_user_by_email(
    email: EmailStr, uow: UnitOfWork = Depends(get_uow)
) -> UserSchema | None:
    return await user_service.read_user_by_email(uow, email)


@router.get(
    "/nickname/{nickname}", response_model=UserSchema, status_code=status.HTTP_200_OK
)
async def read_user_by_nickname(
    nickname: str, uow: UnitOfWork = Depends(get_uow)
) -> UserSchema | None:
    return await user_service.read_user_by_nickname(uow, nickname)


@router.get("/all", response_model=UsersList, status_code=status.HTTP_200_OK)
async def read_all_users(
    offset: int = 0, limit: int = 20, uow: UnitOfWork = Depends(get_uow)
) -> UsersList | None:
    return await user_service.read_all_users(uow, offset, limit)


@router.put(
    "/update/{user_id}", response_model=UserSchema, status_code=status.HTTP_200_OK
)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> UserSchema:
    return await user_service.update_user(uow, user_id, data, current_user_id)


@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> None:
    await user_service.delete_user(uow, user_id, current_user_id)


@router.get(
    "/companies/{user_id}",
    response_model=UserOwnedCompaniesList,
    status_code=status.HTTP_200_OK,
)
async def read_user_companies(
    user_id: UUID, offset: int = 0, limit: int = 20, uow: UnitOfWork = Depends(get_uow)
) -> UserOwnedCompaniesList | None:
    return await user_service.read_user_companies(uow, offset, limit, user_id)
