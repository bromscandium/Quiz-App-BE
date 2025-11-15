from uuid import UUID
from datetime import datetime

from app.schemas.base import Base


class NotificationSchema(Base):
    id: UUID
    company_id: UUID
    message: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class NotificationCreate(Base):
    message: str
    company_id: UUID
