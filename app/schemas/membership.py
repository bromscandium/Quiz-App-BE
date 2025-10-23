from datetime import datetime
from uuid import UUID

from app.schemas.base import Base
from app.models.enums import Roles
from app.schemas.mixins import TimeStamp


class MembershipSchema(Base):
    id: UUID
    company_id: UUID
    user_id: UUID


class MembershipCreateRequest(MembershipSchema):
    role: Roles = Roles.MEMBER
    is_active: bool = True


class MembershipUpdateRequest(Base):
    role: Roles
    is_active: bool | None = None
    left_at: datetime | None = None


class MembershipListResponse(Base):
    memberships: list[MembershipSchema] = []
    total: int = 0


class MembershipDetailResponse(MembershipSchema, TimeStamp):
    role: Roles
    is_active: bool | None = None
    left_at: datetime | None = None
