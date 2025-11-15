from polyfactory.factories.pydantic_factory import ModelFactory
from app.schemas.answer_option import (
    AnswerOptionSchema,
    AnswerOptionCreate,
    AnswerOptionUpdate,
)


class AnswerOptionSchemaFactory(ModelFactory[AnswerOptionSchema]):
    __model__ = AnswerOptionSchema
    __check_model__ = False


class AnswerOptionCreateFactory(ModelFactory[AnswerOptionCreate]):
    __model__ = AnswerOptionCreate
    __check_model__ = False


class AnswerOptionUpdateFactory(ModelFactory[AnswerOptionUpdate]):
    __model__ = AnswerOptionUpdate
    __check_model__ = False
