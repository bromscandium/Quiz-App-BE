from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserSchema(UserBase):
    id: UUID
    email: EmailStr
    name: str
    surname: str | None = None
    nickname: str


class SignUpRequest(UserBase):
    email: EmailStr
    name: str
    surname: str | None = None
    nickname: str
    password: str


class UserUpdateRequest(UserBase):
    email: EmailStr | None = None
    name: str | None = None
    surname: str | None = None
    nickname: str | None = None
    password: str | None = None


class UsersListResponse(UserBase):
    users: list[UserSchema] = []
    total: int = 0


class UserDetailResponse(UserSchema):
    picture: str | None = None
    permissions: list[str] = []
    scope: list[str] = []
    email_verified: bool | None = None
    hashed_password: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None
