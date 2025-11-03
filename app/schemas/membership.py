from datetime import datetime
from uuid import UUID

from app.enums.roles import Roles
from app.schemas.base import Base
from app.schemas.company import CompanySchema
from app.schemas.user import UserSchema


class MembershipSchema(Base):
    id: UUID
    user: UserSchema | None = None
    company: CompanySchema | None = None
    role: Roles
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MembershipCreate(Base):
    user_id: UUID
    company_id: UUID
    role: Roles = Roles.MEMBER
    is_active: bool = True


class MembershipUpdate(Base):
    role: Roles
    is_active: bool | None = None


class MembershipsList(Base):
    total: int = 0
    active_total: int = 0


class UserMembership(Base):
    id: UUID
    company: CompanySchema | None = None
    role: Roles
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserMembershipsList(MembershipsList):
    memberships: list[UserMembership] = []


class CompanyMembership(Base):
    id: UUID
    user: UserSchema | None = None
    role: Roles
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CompanyMembershipsList(MembershipsList):
    memberships: list[CompanyMembership] = []
