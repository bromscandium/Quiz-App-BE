from datetime import datetime
from uuid import UUID

from pydantic import EmailStr

from app.schemas.base import Base
from app.models.enums import Statuses
from app.schemas.mixins import TimeStamp


class InvitationSchema(Base):
    company_id: UUID
    user_id: UUID | None = None
    invited_email: EmailStr | None = None
    status: Statuses = Statuses.PENDING


class InvitationUpdateRequest(InvitationSchema):
    decision_time: datetime | None = None


class InvitationDetailResponse(InvitationSchema, TimeStamp):
    id: UUID
    status: Statuses
    decision_time: datetime | None = None
    expires_at: datetime | None = None


class InvitationListResponse(Base):
    invitations: list[InvitationDetailResponse] = []
    total: int = 0
