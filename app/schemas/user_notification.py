from datetime import datetime
from uuid import UUID

from app.enums import NotificationStatuses
from app.schemas.base import Base
from app.schemas.notification import NotificationSchema
from app.schemas.user import UserSchema


class UserNotificationSchema(Base):
    id: UUID
    notification_id: UUID
    notification: NotificationSchema
    user_id: UUID
    user: UserSchema
    status: NotificationStatuses
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserNotificationsList(Base):
    notifications: list[UserNotificationSchema] = []
    total: int = 0


class UserNotificationUpdate(Base):
    user_id: UUID
    notification_id: UUID
    status: NotificationStatuses
