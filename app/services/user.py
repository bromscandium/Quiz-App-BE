from uuid import UUID

from pydantic import EmailStr

from app.exceptions import UnauthorizedUserAction, UserAlreadyExists, UserNotFound, NicknameTaken
from app.schemas.user import (
    UserCreate,
    UserOwnedCompaniesList,
    UserOwnedCompany,
    UserSchema,
    UsersList,
    UserUpdate,
)
from app.unit_of_work import UnitOfWork
from app.utils import LoggerUtil, PasswordUtil


class UserService:
    def __init__(self):
        self.password_util = PasswordUtil()
        self.logger_util = LoggerUtil()

    async def create_user(self, uow: UnitOfWork, data: UserCreate) -> UserSchema:
        users, _ = await uow.users.read("email", data.email, offset=0, limit=1)
        if users:
            self.logger_util.info("User already exists")
            raise UserAlreadyExists

        users, _ = await uow.users.read("nickname", data.nickname, offset=0, limit=1)
        if users:
            self.logger_util.info("Nickname already exists")
            raise NicknameTaken

        user_data = data.model_dump(exclude={"password"})
        user_data["hashed_password"] = self.password_util.hash_password(data.password)
        user = await uow.users.create(**user_data)
        await uow.session.flush()
        return UserSchema.model_validate(user)

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
        users, total = await uow.users.read(offset=offset, limit=limit)
        user_schemas = [UserSchema.model_validate(u) for u in users]
        return UsersList(users=user_schemas, total=total)

    async def read_user_companies(
            self, uow: UnitOfWork, offset: int = 0, limit: int = 20, value: UUID = None
    ) -> UserOwnedCompaniesList | None:
        items, total = await uow.company.read(
            field="owner_id", value=value, offset=offset, limit=limit
        )

        owned_companies = [UserOwnedCompany.model_validate(c) for c in items]
        return UserOwnedCompaniesList(companies=owned_companies, total=total)

    async def update_user(
            self,
            uow: UnitOfWork,
            user_id: UUID,
            data: UserUpdate,
            current_user_id: UUID,
    ) -> UserSchema:
        if user_id != current_user_id:
            self.logger_util.info("User not authorized")
            raise UnauthorizedUserAction
        if await self.read_user_by_id(uow, user_id) is None:
            self.logger_util.info("User not found")
            raise UserNotFound

        update_data = data.model_dump(exclude_unset=True)
        if update_data.get("password") is not None:
            update_data["hashed_password"] = self.password_util.hash_password(
                update_data["password"]
            )
            del update_data["password"]
        user = await uow.users.update_by("id", user_id, **update_data)
        return UserSchema.model_validate(user)

    async def delete_user(
            self,
            uow: UnitOfWork,
            user_id: UUID,
            current_user_id: UUID,
    ) -> None:
        if user_id != current_user_id:
            self.logger_util.info("User not authorized")
            raise UnauthorizedUserAction

        if await self.read_user_by_id(uow, user_id) is None:
            self.logger_util.info("User not found")
            raise UserNotFound

        await uow.users.delete_by("id", user_id)
