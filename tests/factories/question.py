from polyfactory.factories.pydantic_factory import ModelFactory
from app.schemas.question import (
    QuestionSchema,
    QuestionCreate,
    QuestionsListCreate,
    QuestionUpdate,
)


class QuestionSchemaFactory(ModelFactory[QuestionSchema]):
    __model__ = QuestionSchema
    __check_model__ = False


class QuestionCreateFactory(ModelFactory[QuestionCreate]):
    __model__ = QuestionCreate
    __check_model__ = False


class QuestionsListCreateFactory(ModelFactory[QuestionsListCreate]):
    __model__ = QuestionsListCreate
    __check_model__ = False


class QuestionUpdateFactory(ModelFactory[QuestionUpdate]):
    __model__ = QuestionUpdate
    __check_model__ = False
