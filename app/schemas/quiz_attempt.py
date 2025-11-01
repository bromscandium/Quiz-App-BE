from datetime import datetime
from uuid import UUID

from app.schemas.base import Base
from app.schemas.company import CompanySchema
from app.schemas.quiz import QuizSchema
from app.schemas.user import UserSchema
from app.schemas.user_answer import UserAnswerCreate, UserAnswerSchema


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
