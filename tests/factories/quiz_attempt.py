from polyfactory.factories.pydantic_factory import ModelFactory
from app.schemas.quiz_attempt import (
    QuizAttemptSchema,
    QuizAttemptCreate,
    QuizAttemptsList,
)


class QuizAttemptSchemaFactory(ModelFactory[QuizAttemptSchema]):
    __model__ = QuizAttemptSchema
    __check_model__ = False


class QuizAttemptCreateFactory(ModelFactory[QuizAttemptCreate]):
    __model__ = QuizAttemptCreate
    __check_model__ = False


class QuizAttemptsListFactory(ModelFactory[QuizAttemptsList]):
    __model__ = QuizAttemptsList
    __check_model__ = False
