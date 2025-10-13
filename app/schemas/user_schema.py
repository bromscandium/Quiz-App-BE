from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserSchema(UserBase):
    id: UUID
    email: EmailStr
    name: str
    surname: Optional[str]
    nickname: str


class SignInRequest(UserBase):
    email: EmailStr
    password: str


class SignUpRequest(UserBase):
    email: EmailStr
    name: str
    surname: Optional[str]
    nickname: str
    password: str


class UserUpdateRequest(UserBase):
    email: Optional[EmailStr]
    name: Optional[str]
    surname: Optional[str]
    nickname: Optional[str]
    password: Optional[str]


class UsersListResponse(UserBase):
    users: List[UserSchema]


class UserDetailResponse(UserSchema):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
