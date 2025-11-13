from uuid import UUID

from app.exceptions import NotificationNotFound, UnauthorizedUserAction
from app.models import UserNotification
from app.schemas.notification import (
    NotificationSchema,
    NotificationCreate,
)
from app.schemas.user_notification import (
    UserNotificationsList,
    UserNotificationSchema,
    UserNotificationUpdate,
)
from app.unit_of_work import UnitOfWork
from app.utils import LoggerUtil


class NotificationService:
    def __init__(self):
        self.logger_util = LoggerUtil()
        self.user_notification = UserNotification()

    async def create_notification(
        self, uow: UnitOfWork, data: NotificationCreate
    ) -> NotificationSchema:
        notification = await uow.notifications.create(**data.model_dump())
        await uow.session.flush()
        return NotificationSchema.model_validate(notification)

    async def read_notification_by_id(
        self, uow: UnitOfWork, notification_id: UUID
    ) -> NotificationSchema | None:
        notification, _ = await uow.notifications.read(
            field="id", value=notification_id, offset=0, limit=1
        )
        if not notification:
            return None
        return NotificationSchema.model_validate(notification[0])

    async def read_user_notifications(
        self,
        uow: UnitOfWork,
        user_id: UUID,
        current_user_id,
        offset: int = 0,
        limit: int = 20,
    ) -> UserNotificationsList:
        if user_id != current_user_id:
            self.logger_util.info("User not authorized")
            raise UnauthorizedUserAction
        notifications, total = await uow.user_notifications.read(
            field="user_id",
            value=user_id,
            offset=offset,
            limit=limit,
            load_relationships=["user", "notification"],
        )
        notification_schemas = [
            UserNotificationSchema.model_validate(n) for n in notifications
        ]
        return UserNotificationsList(notifications=notification_schemas, total=total)

    async def update_notification(
        self,
        uow: UnitOfWork,
        current_user_id: UUID,
        data: UserNotificationUpdate,
    ) -> UserNotificationSchema:
        if data.user_id != current_user_id:
            self.logger_util.info("User not authorized")
            raise UnauthorizedUserAction
        user_notifications, _ = await uow.user_notifications.read(
            field="user_id",
            value=data.user_id,
            offset=0,
            limit=100,
            load_relationships=["notification"],
        )

        user_notification = next(
            (
                u_n
                for u_n in user_notifications
                if u_n.notification_id == data.notification_id
            ),
            None,
        )

        if not user_notification:
            self.logger_util.info("Notification not found")
            raise NotificationNotFound

        await uow.user_notifications.update_by(
            "id", user_notification.id, status=data.status
        )
        await uow.session.flush()

        return UserNotificationSchema.model_validate(user_notification)

    async def delete_notification(
        self,
        uow: UnitOfWork,
        current_user_id: UUID,
        user_id: UUID,
        notification_id: UUID,
    ) -> None:
        if user_id != current_user_id:
            self.logger_util.info("User not authorized")
            raise UnauthorizedUserAction

        user_notifications, _ = await uow.user_notifications.read(
            field="user_id",
            value=user_id,
            offset=0,
            limit=100,
            load_relationships=["notification"],
        )

        user_notification = next(
            (
                u_n
                for u_n in user_notifications
                if u_n.notification_id == notification_id
            ),
            None,
        )

        if not user_notification:
            self.logger_util.info("Notification not found")
            raise NotificationNotFound

        await uow.user_notifications.delete_by("id", user_notification.id)
