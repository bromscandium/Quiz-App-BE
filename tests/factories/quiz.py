from polyfactory.factories.pydantic_factory import ModelFactory
from app.schemas.quiz import (
    QuizSchema,
    QuizCreate,
    QuizUpdate,
    QuizUpdateWithQuestions,
    QuizList,
)


class QuizSchemaFactory(ModelFactory[QuizSchema]):
    __model__ = QuizSchema
    __check_model__ = False


class QuizCreateFactory(ModelFactory[QuizCreate]):
    __model__ = QuizCreate
    __check_model__ = False


class QuizUpdateFactory(ModelFactory[QuizUpdate]):
    __model__ = QuizUpdate
    __check_model__ = False


class QuizUpdateWithQuestionsFactory(ModelFactory[QuizUpdateWithQuestions]):
    __model__ = QuizUpdateWithQuestions
    __check_model__ = False


class QuizListFactory(ModelFactory[QuizList]):
    __model__ = QuizList
    __check_model__ = False
