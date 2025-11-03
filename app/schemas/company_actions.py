from datetime import datetime
from uuid import UUID

from pydantic import EmailStr

from app.enums.action_types import ActionTypes
from app.enums.action_statuses import ActionStatuses
from app.schemas.base import Base
from app.schemas.company import CompanySchema
from app.schemas.user import UserSchema


class CompanyActionSchema(Base):
    id: UUID
    user: UserSchema | None = None
    company: CompanySchema | None = None
    action_type: ActionTypes
    invited_email: EmailStr | None = None
    status: ActionStatuses
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CompanyActionCreate(Base):
    user_id: UUID
    company_id: UUID
    action_type: ActionTypes
    invited_email: EmailStr | None = None
    status: ActionStatuses = ActionStatuses.PENDING


class CompanyActionUpdate(Base):
    status: ActionStatuses = ActionStatuses.PENDING


class CompanyActionsList(Base):
    actions: list[CompanyActionSchema]
    total: int
    pending_total: int
    accepted_total: int
    cancelled_total: int
