from datetime import datetime, date
from uuid import UUID

from pydantic import EmailStr

from app.schemas.base import Base


class UserSchema(Base):
    id: UUID
    name: str
    surname: str | None = None
    nickname: str
    email: EmailStr
    hashed_password: str
    avatar_url: str | None = None
    bio: str | None = None
    birthday: date | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

class UserCreate(Base):
    name: str
    surname: str | None = None
    nickname: str
    email: EmailStr
    password: str


class UserUpdate(Base):
    name: str | None = None
    surname: str | None = None
    nickname: str | None = None
    password: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    birthday: date | None = None


class UsersList(Base):
    users: list[UserSchema] = []
    total: int = 0


class UserOwnedCompany(Base):
    id: UUID
    name: str
    description: str | None = None
    visibility: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserOwnedCompaniesList(Base):
    companies: list[UserOwnedCompany] = []
    total: int = 0
