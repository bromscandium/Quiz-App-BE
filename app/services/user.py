from pydantic import EmailStr
from uuid import UUID

from app.exceptions.base import InternalErrorException
from app.unit_of_work.uow import UnitOfWork
from app.utils.password import PasswordUtil
from app.schemas.user import (
    UserSchema,
    UserCreate,
    UserUpdate,
    UsersList,
    UserOwnedCompaniesList,
    UserOwnedCompany,
)
from app.utils.logger import logger
from app.exceptions.user import UserAlreadyExists, UnauthorizedUserAction


class UserService:
    def __init__(self):
        self.password_util = PasswordUtil()

    async def create_user(self, uow: UnitOfWork, data: UserCreate) -> UserSchema:
        try:
            items, _ = await uow.users.read("email", data.email, offset=0, limit=1)
            if items:
                raise UserAlreadyExists

            user_data = data.model_dump(exclude={"password"})
            user_data["hashed_password"] = self.password_util.hash_password(
                data.password
            )
            user = await uow.users.create(**user_data)
            await uow.session.flush()
            return UserSchema.model_validate(user)

        except UserAlreadyExists:
            raise
        except Exception as e:
            logger.exception(f"Error while creating user: {e}")
            raise InternalErrorException

    async def read_user_by_id(self, uow: UnitOfWork, value: UUID) -> UserSchema | None:
        user, _ = await uow.users.read(field="id", value=value, offset=0, limit=1)
        if not user:
            return None
        return UserSchema.model_validate(user[0])

    async def read_user_by_email(
        self, uow: UnitOfWork, value: EmailStr
    ) -> UserSchema | None:
        user, _ = await uow.users.read(field="email", value=value, offset=0, limit=1)
        if not user:
            return None
        return UserSchema.model_validate(user[0])

    async def read_user_by_nickname(
        self, uow: UnitOfWork, value: str
    ) -> UserSchema | None:
        user, _ = await uow.users.read(field="nickname", value=value, offset=0, limit=1)
        if not user:
            return None
        return UserSchema.model_validate(user[0])

    async def read_all_users(
        self, uow: UnitOfWork, offset: int = 0, limit: int = 20
    ) -> UsersList | None:
        items, total = await uow.users.read(offset=offset, limit=limit)
        user_schemas = [UserSchema.model_validate(u) for u in items]
        return UsersList(users=user_schemas, total=total)

    async def update_user(
        self,
        uow: UnitOfWork,
        user_id: UUID,
        data: UserUpdate,
        current_user_id: UUID,
    ) -> UserSchema:
        try:
            if user_id != current_user_id:
                raise UnauthorizedUserAction

            update_data = data.model_dump(exclude_unset=True)
            if "password" in update_data:
                update_data["hashed_password"] = self.password_util.hash_password(
                    update_data["password"]
                )
                del update_data["password"]
            user = await uow.users.update_by("id", user_id, **update_data)
            return UserSchema.model_validate(user)
        except UnauthorizedUserAction:
            raise
        except Exception as e:
            logger.exception(f"Error while updating user: {e}")
            raise InternalErrorException

    async def delete_user(
        self,
        uow: UnitOfWork,
        user_id: UUID,
        current_user_id: UUID,
    ) -> None:
        try:
            if user_id != current_user_id:
                raise UnauthorizedUserAction
            await self.read_user_by_id(uow, user_id)
            await uow.users.delete_by("id", user_id)
        except UnauthorizedUserAction:
            raise
        except Exception as e:
            logger.exception(f"Error while deleting user: {e}")
            raise InternalErrorException

    async def read_user_companies(
        self, uow: UnitOfWork, offset: int = 0, limit: int = 20, value: UUID = None
    ) -> UserOwnedCompaniesList | None:
        items, total = await uow.company.read(
            field="owner_id", value=value, offset=offset, limit=limit
        )

        owned_companies = [UserOwnedCompany.model_validate(c) for c in items]
        return UserOwnedCompaniesList(companies=owned_companies, total=total)
