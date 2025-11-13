from polyfactory.factories.pydantic_factory import ModelFactory
from app.schemas.user_notification import (
    UserNotificationSchema,
    UserNotificationsList,
    UserNotificationUpdate,
)


class UserNotificationSchemaFactory(ModelFactory[UserNotificationSchema]):
    __model__ = UserNotificationSchema
    __check_model__ = False


class UserNotificationsListFactory(ModelFactory[UserNotificationsList]):
    __model__ = UserNotificationsList
    __check_model__ = False


class UserNotificationUpdateFactory(ModelFactory[UserNotificationUpdate]):
    __model__ = UserNotificationUpdate
    __check_model__ = False
