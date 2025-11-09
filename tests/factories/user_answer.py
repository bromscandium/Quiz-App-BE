from polyfactory.factories.pydantic_factory import ModelFactory
from app.schemas.user_answer import UserAnswerSchema, UserAnswerCreate


class UserAnswerSchemaFactory(ModelFactory[UserAnswerSchema]):
    __model__ = UserAnswerSchema
    __check_model__ = False


class UserAnswerCreateFactory(ModelFactory[UserAnswerCreate]):
    __model__ = UserAnswerCreate
    __check_model__ = False
