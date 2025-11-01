from datetime import datetime
from uuid import UUID

from app.schemas.base import Base


class UserStats(Base):
    user_id: UUID
    company_id: UUID | None = None
    total_correct_answers: int
    total_answered_questions: int
    average_score: float

    last_attempt_at: datetime | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
