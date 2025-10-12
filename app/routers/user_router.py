from fastapi import APIRouter, Depends

from app.exceptions.user_exceptions import *
from app.models import User
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

router = APIRouter(prefix="/users", tags=["users"])


async def get_uow():
    async with UnitOfWork(async_session) as uow:
        yield uow


@router.post(
    "/",
    response_model=UserDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Creates a new user in the system. Raises 400 if user already exists or validation fails.",
)
async def create_user(data: SignUpRequest, uow: UnitOfWork = Depends(get_uow)) -> User:
    try:
        return await UserService.create_user(uow, data)
    except ValueError:
        raise UserAlreadyExistsException()
    except Exception as e:
        raise UserInternalErrorException(str(e))


@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Fetches a user by their unique ID. Returns 404 if the user does not exist.",
)
async def get_user_by_id(
    user_id: int, uow: UnitOfWork = Depends(get_uow)
) -> UserDetailResponse | None:
    user = await UserService.get_user_by_id(uow, user_id)
    if not user:
        raise UserNotFoundException()
    return user


@router.get(
    "/",
    response_model=UsersListResponse,
    status_code=status.HTTP_200_OK,
    summary="List users",
    description="Returns a paginated list of users. Supports offset and limit for pagination.",
)
async def read_all_users(
    offset: int = 0, limit: int = 20, uow: UnitOfWork = Depends(get_uow)
) -> UsersListResponse:
    try:
        return await UserService.read_all_users(uow, offset, limit)
    except Exception:
        raise UserInternalErrorException("Failed to fetch users")


@router.put(
    "/{user_id}",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    summary="Update user",
    description="Updates a user's details by their ID. Returns 404 if the user does not exist.",
)
async def update_user(
    user_id: int, data: UserUpdateRequest, uow: UnitOfWork = Depends(get_uow)
) -> UserSchema:
    try:
        user = await UserService.update_user(uow, user_id, data)
    except ValueError:
        raise UserAlreadyExistsException()
    except Exception as e:
        raise UserInternalErrorException(str(e))

    if not user:
        raise UserNotFoundException()

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Deletes a user by their ID. Returns 404 if the user does not exist.",
)
async def delete_user(user_id: int, uow: UnitOfWork = Depends(get_uow)) -> None:
    try:
        await UserService.delete_user(uow, user_id)
    except ValueError:
        raise UserNotFoundException()
    except Exception as e:
        raise UserInternalErrorException(str(e))
