from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from app.models.user_model import User
from app.services.refresh_token_service import RefreshTokenService
from app.unit_of_work.uow import UnitOfWork
from app.utils.password_util import PasswordUtil
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
    def __init__(self, refresh_token: RefreshTokenService):
        self.refresh_token = refresh_token

    async def create_user(self, uow: UnitOfWork, data: SignUpRequest) -> User:
        try:
            existing = await uow.users.read_by("email", data.email)
            if existing:
                raise UserAlreadyExistsException()

            user_data = data.model_dump(exclude={"password"})
            user_data["hashed_password"] = PasswordUtil().hash_password(data.password)
            user = await uow.users.create(**user_data)
            await uow.commit()
            logger.info("User created")
            return user

        except UserAlreadyExistsException:
            await uow.rollback()
            raise
        except IntegrityError as e:
            await uow.rollback()
            logger.exception(f"DB integrity error while creating user: {e}")
            raise UserAlreadyExistsException()
        except Exception as e:
            await uow.rollback()
            logger.exception(f"Error while creating user: {e}")
            raise UserInternalErrorException(str(e))

    async def get_user_by_id(
        self, uow: UnitOfWork, user_id: UUID
    ) -> UserDetailResponse:
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

    async def get_user_by_email(
        self, uow: UnitOfWork, email: EmailStr
    ) -> UserDetailResponse | None:
        try:
            user = await uow.users.read_by("email", email)
            if not user:
                return None
            return UserDetailResponse.model_validate(user)
        except UserNotFoundException:
            raise
        except Exception as e:
            logger.exception(f"Error while fetching user by email: {e}")
            raise UserInternalErrorException(str(e))

    async def read_all_users(
        self, uow: UnitOfWork, offset: int = 0, limit: int = 20
    ) -> UsersListResponse:
        try:
            users = await uow.users.read_all(offset=offset, limit=limit)
            user_schemas = [UserSchema.model_validate(user) for user in users]
            return UsersListResponse(users=user_schemas)
        except Exception as e:
            logger.exception(f"Error while fetching list of users: {e}")
            raise UserInternalErrorException("Failed to fetch users")

    async def update_user(
        self, uow: UnitOfWork, user_id: UUID, data: UserUpdateRequest
    ) -> UserSchema:
        try:
            existing_user = await uow.users.read_by("id", user_id)
            if not existing_user:
                raise UserNotFoundException()

            update_data = data.model_dump(exclude_unset=True)

            if "password" in update_data:
                update_data["hashed_password"] = PasswordUtil().hash_password(
                    data.password
                )
                del update_data["password"]

            user = await uow.users.update_by("id", user_id, **update_data)
            await uow.commit()
            logger.info(f"User updated")
            return UserSchema.model_validate(user)

        except UserNotFoundException:
            await uow.rollback()
            raise
        except IntegrityError as e:
            await uow.rollback()
            logger.exception(f"DB integrity error while updating user: {e}")
            raise UserAlreadyExistsException()
        except Exception as e:
            await uow.rollback()
            logger.exception(f"Error while updating user: {e}")
            raise UserInternalErrorException(str(e))

    async def delete_user(self, uow: UnitOfWork, user_id: UUID) -> None:
        try:
            user = await uow.users.read_by("id", user_id)
            if not user:
                raise UserNotFoundException()
            await self.refresh_token.delete_refresh_token(uow, user_id)
            await uow.users.delete_by("id", user_id)
            await uow.commit()
            logger.info(f"User deleted")

        except UserNotFoundException:
            await uow.rollback()
            raise
        except Exception as e:
            await uow.rollback()
            logger.exception(f"Error while deleting user: {e}")
            raise UserInternalErrorException(str(e))
