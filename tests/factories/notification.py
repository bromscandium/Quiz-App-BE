from polyfactory.factories.pydantic_factory import ModelFactory
from app.schemas.notification import NotificationSchema, NotificationCreate


class NotificationSchemaFactory(ModelFactory[NotificationSchema]):
    __model__ = NotificationSchema
    __check_model__ = False


class NotificationCreateFactory(ModelFactory[NotificationCreate]):
    __model__ = NotificationCreate
    __check_model__ = False
