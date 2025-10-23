from datetime import datetime
from uuid import UUID

from app.schemas.base import Base
from app.models.enums import Statuses
from app.schemas.mixins import TimeStamp


class RequestSchema(Base):
    company_id: UUID
    user_id: UUID | None = None
    status: Statuses = Statuses.PENDING


class RequestUpdateRequest(RequestSchema):
    decision_time: datetime | None = None


class RequestDetailResponse(RequestSchema, TimeStamp):
    id: UUID
    status: Statuses
    decision_time: datetime | None = None
    expires_at: datetime | None = None


class RequestsListResponse(Base):
    requests: list[RequestDetailResponse] = []
    total: int = 0
