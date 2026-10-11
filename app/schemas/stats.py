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


class UserQuizStats(Base):
    quiz_id: UUID
    quiz_title: str
    average_score: float
    attempts_count: int
    last_attempt_at: datetime


class UserStatsQuizzesList(Base):
    user_attempts: list[UserQuizStats] = []


class UserLastAttempt(Base):
    quiz_id: UUID
    quiz_title: str
    last_attempt_at: datetime


class UserLastAttemptsList(Base):
    user_attempts: list[UserLastAttempt] = []


class CompanyUserStats(Base):
    user_id: UUID
    user_name: str
    average_score: float
    total_attempts: int
    last_attempt_at: datetime | None = None


class CompanyUserStatsList(Base):
    user_stats: list[CompanyUserStats] = []


class CompanyUserQuizStats(Base):
    quiz_id: UUID
    quiz_title: str
    average_score: float
    attempts_count: int
    last_attempt_at: datetime | None = None


class CompanyUserQuizStatsList(Base):
    quiz_stats: list[CompanyUserQuizStats] = []


class CompanyUserLastAttempt(Base):
    user_id: UUID
    user_name: str
    last_attempt_at: datetime | None = None


class CompanyUserLastAttemptsList(Base):
    user_attempts: list[CompanyUserLastAttempt] = []
