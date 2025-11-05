from app.models.user_notification import UserNotification
from app.repositories.base import BaseRepository


class UserNotificationRepository(BaseRepository[UserNotification]):
    def __init__(self, session):
        super().__init__(session, UserNotification)
