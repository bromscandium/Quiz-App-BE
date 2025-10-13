from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from uuid import UUID
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
from app.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    UserInternalErrorException,
)


class UserService:
    @staticmethod
    async def create_user(uow: UnitOfWork, data: SignUpRequest) -> User:
        try:
            existing = await uow.users.read_by("email", data.email)
            if existing:
                raise UserAlreadyExistsException()

            user_data = data.model_dump(exclude={"password"})
            user_data["hashed_password"] = PasswordService().hash_password(
                data.password
            )
            user = await uow.users.create(**user_data)
            await uow.commit()
            logger.info("User created")
            return user

        except UserAlreadyExistsException:
            raise
        except IntegrityError as e:
            await uow.rollback()
            logger.exception(f"DB integrity error while creating user: {e}")
            raise UserAlreadyExistsException()
        except Exception as e:
            await uow.rollback()
            logger.exception(f"Error while creating user: {e}")
            raise UserInternalErrorException(str(e))

    @staticmethod
    async def get_user_by_id(uow: UnitOfWork, user_id: UUID) -> UserDetailResponse:
        try:
            user = await uow.users.read_by("id", user_id)
            if not user:
                raise UserNotFoundException()
            return UserDetailResponse.model_validate(user)
        except UserNotFoundException:
            raise
        except Exception as e:
            logger.exception(f"Error while fetching user by id: {e}")
            raise UserInternalErrorException(str(e))

    @staticmethod
    async def get_user_by_email(uow: UnitOfWork, email: EmailStr) -> UserDetailResponse:
        try:
            user = await uow.users.read_by("email", email)
            if not user:
                raise UserNotFoundException()
            return UserDetailResponse.model_validate(user)
        except UserNotFoundException:
            raise
        except Exception as e:
            logger.exception(f"Error while fetching user by email: {e}")
            raise UserInternalErrorException(str(e))

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
            raise UserInternalErrorException("Failed to fetch users")

    @staticmethod
    async def update_user(
        uow: UnitOfWork, user_id: UUID, data: UserUpdateRequest
    ) -> UserSchema:
        try:
            existing_user = await uow.users.read_by("id", user_id)
            if not existing_user:
                raise UserNotFoundException()

            update_data = data.model_dump(exclude_unset=True)

            if "password" in update_data:
                update_data["hashed_password"] = PasswordService().hash_password(
                    data.password
                )
                del update_data["password"]

            user = await uow.users.update_by("id", user_id, **update_data)
            await uow.commit()
            logger.info(f"User updated")
            return UserSchema.model_validate(user)

        except UserNotFoundException:
            raise
        except IntegrityError as e:
            await uow.rollback()
            logger.exception(f"DB integrity error while updating user: {e}")
            raise UserAlreadyExistsException()
        except Exception as e:
            await uow.rollback()
            logger.exception(f"Error while updating user: {e}")
            raise UserInternalErrorException(str(e))

    @staticmethod
    async def delete_user(uow: UnitOfWork, user_id: UUID) -> None:
        try:
            user = await uow.users.read_by("id", user_id)
            if not user:
                raise UserNotFoundException()

            await uow.users.delete_by("id", user_id)
            await uow.commit()
            logger.info(f"User deleted")

        except UserNotFoundException:
            raise
        except Exception as e:
            await uow.rollback()
            logger.exception(f"Error while deleting user: {e}")
            raise UserInternalErrorException(str(e))
