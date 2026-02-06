from uuid import UUID
from datetime import datetime

from app.schemas.base import Base
from app.schemas.company import CompanySchema
from app.schemas.quiz import QuizSchema
from app.schemas.user import UserSchema
from app.schemas.user_answer import UserAnswerSchema, UserAnswerCreate


class QuizAttemptSchema(Base):
    id: UUID
    user_id: UUID
    company_id: UUID
    quiz_id: UUID
    correct_answers: int
    total_questions: int
    user_answers: list[UserAnswerSchema] = []
    user: UserSchema | None = None
    company: CompanySchema | None = None
    quiz: QuizSchema | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class QuizAttemptCreate(Base):
    quiz_id: UUID
    company_id: UUID
    user_answers: list[UserAnswerCreate] = []


class QuizAttemptsList(Base):
    quiz_attempts: list[QuizAttemptSchema] = []
    total: int


class UserStats(Base):
    user_id: UUID
    company_id: UUID | None = None
    total_correct_answers: int
    total_answered_questions: int
    average_score: float

    last_attempt_at: datetime | None = None
