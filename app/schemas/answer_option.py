from datetime import datetime
from uuid import UUID

from app.schemas.base import Base


class AnswerOptionSchema(Base):
    id: UUID
    question_id: UUID
    text: str
    is_correct: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AnswerOptionCreate(Base):
    text: str
    is_correct: bool


class AnswerOptionUpdate(Base):
    id: UUID | None = None
    text: str
    is_correct: bool
