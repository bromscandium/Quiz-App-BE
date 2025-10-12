from typing import Optional, Any, Coroutine
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError

from app.models.user_model import User
from app.unit_of_work.uow import UnitOfWork
from app.utils.password_service import PasswordService
from app.schemas.user_schema import (
    SignUpRequest,
    UserUpdateRequest,
    UserSchema,
    UsersListResponse,
    UserDetailResponse,
)
from app.utils.logger import logger


class UserService:
    @staticmethod
    async def create_user(uow: UnitOfWork, data: SignUpRequest) -> User:
        existing = await uow.users.read_by("email", data.email)
        if existing:
            raise ValueError("User already exists")

        try:
            user_data = data.model_dump(exclude={"password"})
            user_data["hashed_password"] = PasswordService().hash_password(
                data.password
            )
            user = await uow.users.create(**user_data)
            await uow.commit()
            logger.info("User created")
            return user

        except IntegrityError as e:
            await uow.rollback()
            logger.exception(f"DB integrity error while creating user: {e}")
            raise ValueError("Failed to create user")

    @staticmethod
    async def get_user_by_id(
        uow: UnitOfWork, user_id: int
    ) -> UserDetailResponse | None:
        try:
            user = await uow.users.read_by("id", user_id)
            return UserDetailResponse.model_validate(user)
        except Exception as e:
            logger.exception(f"Error while fetching user by id: {e}")
            return None

    @staticmethod
    async def get_user_by_email(
        uow: UnitOfWork, email: EmailStr
    ) -> UserDetailResponse | None:
        try:
            user = await uow.users.read_by("email", email)
            return UserDetailResponse.model_validate(user)
        except Exception as e:
            logger.exception(f"Error while fetching user by email: {e}")
            return None

    @staticmethod
    async def read_all_users(
        uow: UnitOfWork, offset: int = 0, limit: int = 20
    ) -> UsersListResponse:
        try:
            users = await uow.users.read_all(offset=offset, limit=limit)
            user_schemas = [UserSchema.model_validate(user) for user in users]
            return UsersListResponse(users=user_schemas)
        except Exception as e:
            logger.exception(f"Error while fetching list of users: {e}")
            raise ValueError("Failed to fetch list of users")

    @staticmethod
    async def update_user(
        uow: UnitOfWork, user_id: int, data: UserUpdateRequest
    ) -> UserSchema:
        update_data = data.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = PasswordService().hash_password(
                data.password
            )

        try:
            user = await uow.users.update_by("id", user_id, **update_data)
            if user:
                await uow.commit()
            logger.info(f"User updated")
            return UserSchema.model_validate(user)
        except IntegrityError as e:
            await uow.rollback()
            logger.exception(f"DB integrity error while updating user: {e}")
            raise ValueError("Failed to update user")

    @staticmethod
    async def delete_user(uow: UnitOfWork, user_id: int) -> None:
        user = await uow.users.read_by("id", user_id)
        if not user:
            raise ValueError("User not found")
        try:
            await uow.users.delete_by("id", user_id)
            await uow.commit()
            logger.info(f"User deleted")
        except Exception as e:
            await uow.rollback()
            logger.exception(f"Error while deleting user: {e}")
            raise ValueError("Failed to delete user")
