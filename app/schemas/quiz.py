from datetime import datetime
from uuid import UUID

from app.schemas.base import Base
from app.schemas.question import QuestionSchema, QuestionUpdate


class QuizSchema(Base):
    id: UUID
    company_id: UUID
    title: str
    description: str | None = None
    frequency: int
    questions: list[QuestionSchema] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class QuizCreate(Base):
    company_id: UUID
    title: str
    description: str | None = None


class QuizUpdateWithQuestions(Base):
    questions: list[QuestionUpdate] = []


class QuizUpdate(QuizUpdateWithQuestions):
    title: str | None = None
    description: str | None = None
    frequency: int | None = None


class QuizList(Base):
    quizzes: list[QuizSchema]
    total: int
