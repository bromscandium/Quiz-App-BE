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
    surname: Optional[str] = None
    nickname: str


class SignUpRequest(UserBase):
    email: EmailStr
    name: str
    surname: Optional[str] = None
    nickname: str
    password: str


class UserUpdateRequest(UserBase):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    nickname: Optional[str] = None
    password: Optional[str] = None


class UsersListResponse(UserBase):
    users: List[UserSchema] = []


class UserDetailResponse(UserSchema):
    sub: Optional[str] = None
    picture: Optional[str] = None
    permissions: List[str] = []
    scope: List[str] = []
    email_verified: Optional[bool] = None
    hashed_password: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
