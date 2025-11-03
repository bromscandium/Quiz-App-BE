import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Enum as SQLAEnum

from app.enums import NotificationStatuses
from app.models import Base


class UserNotification(Base):
    __tablename__ = "user_notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
        nullable=False,
    )

    notification_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notifications.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
        nullable=False,
    )

    status: Mapped[NotificationStatuses] = mapped_column(
        SQLAEnum(NotificationStatuses, name="notification_statuses", create_type=False),
        index=True,
        nullable=False,
        default=NotificationStatuses.UNREAD,
    )

    user: Mapped["User"] = relationship(back_populates="notifications")
    notification: Mapped["Notification"] = relationship(back_populates="users")
