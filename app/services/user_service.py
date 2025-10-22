from psycopg2 import IntegrityError
from pydantic import EmailStr
from uuid import UUID

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
    UnauthorizedUserActionException,
)


class UserService:
    def __init__(self):
        self.refresh_token_service = RefreshTokenService()
        self.password_util = PasswordUtil()

    async def create_user(
        self, uow: UnitOfWork, data: SignUpRequest
    ) -> UserDetailResponse:
        try:
            items, _ = await uow.users.read("email", data.email, offset=0, limit=1)
            if items:
                raise UserAlreadyExistsException

            user_data = data.model_dump(exclude={"password"})
            user_data["hashed_password"] = self.password_util.hash_password(
                data.password
            )
            user = await uow.users.create(**user_data)
            await uow.session.flush()
            logger.info("User created")
            return UserDetailResponse.model_validate(user)

        except UserAlreadyExistsException:
            raise UserAlreadyExistsException
        except IntegrityError:
            logger.exception("DB integrity error while creating user")
            raise UserAlreadyExistsException
        except Exception as e:
            logger.exception(f"Error while creating user: {e}")
            raise UserInternalErrorException

    async def get_user_by_id(
        self, uow: UnitOfWork, user_id: UUID
    ) -> UserDetailResponse:
        try:
            user, _ = await uow.users.read(field="id", value=user_id, offset=0, limit=1)
            if not user:
                raise UserNotFoundException
            return UserDetailResponse.model_validate(user[0])
        except Exception as e:
            logger.exception(f"Error while fetching user by id: {e}")
            raise UserInternalErrorException

    async def get_user_by_email(
        self,
        uow: UnitOfWork,
        email: EmailStr,
    ) -> UserDetailResponse | None:
        try:
            items, _ = await uow.users.read(
                field="email", value=email, offset=0, limit=1
            )
            user = items[0] if items else None
            if not user:
                return None
            return UserDetailResponse.model_validate(user)
        except Exception as e:
            logger.exception(f"Error while fetching user by email: {e}")
            raise UserInternalErrorException

    async def read_all_users(
        self, uow: UnitOfWork, offset: int = 0, limit: int = 20
    ) -> UsersListResponse:
        items, total = await uow.users.read(offset=offset, limit=limit)
        user_schemas = [UserSchema.model_validate(user) for user in items]
        return UsersListResponse(users=user_schemas, total=total)

    async def update_user(
        self,
        uow: UnitOfWork,
        user_id: UUID,
        data: UserUpdateRequest,
        current_user_id: UUID,
    ) -> UserDetailResponse:
        try:
            if user_id != current_user_id:
                raise UnauthorizedUserActionException

            update_data = data.model_dump(exclude_unset=True)
            if "password" in update_data:
                update_data["hashed_password"] = PasswordUtil().hash_password(
                    update_data["password"]
                )
                del update_data["password"]
            user = await uow.users.update_by("id", user_id, **update_data)
            logger.info("User updated")
            return UserDetailResponse.model_validate(user)
        except UnauthorizedUserActionException:
            raise UnauthorizedUserActionException
        except IntegrityError:
            logger.exception("DB integrity error while updating user")
            raise UserAlreadyExistsException
        except Exception as e:
            logger.exception(f"Error while updating user: {e}")
            raise UserInternalErrorException

    async def delete_user(
        self,
        uow: UnitOfWork,
        user_id: UUID,
        current_user_id: UUID,
    ) -> None:
        try:
            if user_id != current_user_id:
                raise UnauthorizedUserActionException

            await self.get_user_by_id(uow, user_id)
            await self.refresh_token_service.delete_refresh_token(uow, user_id)
            await uow.users.delete_by("id", user_id)
            logger.info("User deleted")
        except UnauthorizedUserActionException:
            raise UnauthorizedUserActionException
        except Exception as e:
            logger.exception(f"Error while deleting user: {e}")
            raise UserInternalErrorException
