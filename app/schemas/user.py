from uuid import UUID
from pydantic import EmailStr, BaseModel

from app.schemas.base import Base
from app.schemas.mixins import TimeStamp


class UserSchema(Base):
    id: UUID
    email: EmailStr
    name: str
    surname: str | None = None
    nickname: str


class UserCreateRequest(Base):
    email: EmailStr
    name: str
    surname: str | None = None
    nickname: str
    password: str


class UserUpdateRequest(Base):
    name: str | None = None
    surname: str | None = None
    nickname: str | None = None
    password: str | None = None


class UsersListResponse(Base):
    users: list[UserSchema] = []
    total: int = 0


class UserDetailResponse(UserSchema, TimeStamp):
    picture: str | None = None
    permissions: list[str] = []
    scope: list[str] = []
    email_verified: bool | None = None
    hashed_password: str = ""
