from uuid import UUID
from app.schemas.base import Base
from datetime import datetime


class UserAnswerSchema(Base):
    id: UUID
    quiz_attempt_id: UUID
    question_id: UUID
    answer_option_id: UUID
    is_correct: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserAnswerCreate(Base):
    question_id: UUID
    answer_option_id: UUID
