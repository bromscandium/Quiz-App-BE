from uuid import UUID
from datetime import datetime
from app.schemas.base import Base
from app.schemas.answer_option import (
    AnswerOptionSchema,
    AnswerOptionCreate,
    AnswerOptionUpdate,
)


class QuestionSchema(Base):
    id: UUID
    quiz_id: UUID
    title: str
    answer_options: list[AnswerOptionSchema] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class QuestionCreate(Base):
    title: str
    answer_options: list[AnswerOptionCreate]


class QuestionsListCreate(Base):
    questions: list[QuestionCreate]


class QuestionUpdate(Base):
    id: UUID | None = None
    title: str
    answer_options: list[AnswerOptionUpdate]
