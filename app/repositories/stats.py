from datetime import datetime
from uuid import UUID

from sqlalchemy import Row, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.user import User


class StatsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def calculate_stats(
        self,
        user_id: UUID,
        quiz_id: UUID | None = None,
        company_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> Row | None:
        stmt = select(
            func.sum(QuizAttempt.correct_answers).label("total_correct"),
            func.sum(QuizAttempt.total_questions).label("total_questions"),
            func.max(QuizAttempt.updated_at).label("last_attempt"),
        ).where(QuizAttempt.user_id == user_id)

        if company_id:
            stmt = stmt.where(QuizAttempt.company_id == company_id)

        if quiz_id:
            subq = (
                select(func.max(QuizAttempt.created_at))
                .where(QuizAttempt.user_id == user_id)
                .where(QuizAttempt.quiz_id == quiz_id)
                .scalar_subquery()
            )
            stmt = stmt.where(QuizAttempt.created_at == subq).where(
                QuizAttempt.quiz_id == quiz_id
            )

        if start_date:
            stmt = stmt.where(QuizAttempt.created_at >= start_date)

        if end_date:
            stmt = stmt.where(QuizAttempt.created_at <= end_date)

        result = await self.session.execute(stmt)
        return result.first()

    async def calculate_user_quizzes_stats(
        self,
        user_id: UUID,
        company_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[Row] | None:
        stmt = (
            select(
                QuizAttempt.quiz_id,
                Quiz.title.label("quiz_title"),
                func.avg(
                    (QuizAttempt.correct_answers * 100.0) / QuizAttempt.total_questions
                ).label("average_score"),
                func.count(QuizAttempt.id).label("attempts_count"),
                func.max(QuizAttempt.created_at).label("last_attempt_at"),
            )
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
            .where(QuizAttempt.user_id == user_id)
            .group_by(QuizAttempt.quiz_id, Quiz.title)
        )

        if company_id:
            stmt = stmt.where(QuizAttempt.company_id == company_id)

        if start_date:
            stmt = stmt.where(QuizAttempt.created_at >= start_date)

        if end_date:
            stmt = stmt.where(QuizAttempt.created_at <= end_date)

        result = await self.session.execute(stmt)
        return result.all()

    async def get_user_last_attempts(
        self,
        user_id: UUID,
        company_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[Row] | None:
        subq = select(
            QuizAttempt.quiz_id, func.max(QuizAttempt.created_at).label("max_date")
        ).where(QuizAttempt.user_id == user_id)

        if company_id:
            subq = subq.where(QuizAttempt.company_id == company_id)

        if start_date:
            subq = subq.where(QuizAttempt.created_at >= start_date)

        if end_date:
            subq = subq.where(QuizAttempt.created_at <= end_date)

        subq = subq.group_by(QuizAttempt.quiz_id).subquery()

        stmt = (
            select(
                QuizAttempt.quiz_id,
                Quiz.title.label("quiz_title"),
                QuizAttempt.created_at.label("last_attempt_at"),
            )
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
            .join(
                subq,
                (QuizAttempt.quiz_id == subq.c.quiz_id)
                & (QuizAttempt.created_at == subq.c.max_date),
            )
            .where(QuizAttempt.user_id == user_id)
        )

        if company_id:
            stmt = stmt.where(QuizAttempt.company_id == company_id)

        result = await self.session.execute(stmt)
        return result.all()

    async def calculate_company_users_stats(
        self,
        company_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[Row] | None:
        stmt = (
            select(
                QuizAttempt.user_id,
                User.name.label("user_name"),
                func.avg(
                    (QuizAttempt.correct_answers * 100.0) / QuizAttempt.total_questions
                ).label("average_score"),
                func.count(QuizAttempt.id).label("total_attempts"),
                func.max(QuizAttempt.created_at).label("last_attempt_at"),
            )
            .join(User, QuizAttempt.user_id == User.id)
            .where(QuizAttempt.company_id == company_id)
            .group_by(QuizAttempt.user_id, User.name)
        )

        if start_date:
            stmt = stmt.where(QuizAttempt.created_at >= start_date)

        if end_date:
            stmt = stmt.where(QuizAttempt.created_at <= end_date)

        result = await self.session.execute(stmt)
        return result.all()

    async def calculate_company_user_quizzes_stats(
        self,
        company_id: UUID,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[Row] | None:
        stmt = (
            select(
                QuizAttempt.quiz_id,
                Quiz.title.label("quiz_title"),
                func.avg(
                    (QuizAttempt.correct_answers * 100.0) / QuizAttempt.total_questions
                ).label("average_score"),
                func.count(QuizAttempt.id).label("attempts_count"),
                func.max(QuizAttempt.created_at).label("last_attempt_at"),
            )
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
            .where(QuizAttempt.company_id == company_id)
            .where(QuizAttempt.user_id == user_id)
            .group_by(QuizAttempt.quiz_id, Quiz.title)
        )

        if start_date:
            stmt = stmt.where(QuizAttempt.created_at >= start_date)

        if end_date:
            stmt = stmt.where(QuizAttempt.created_at <= end_date)

        result = await self.session.execute(stmt)
        return result.all()

    async def get_company_users_last_attempts(
        self,
        company_id: UUID,
    ) -> list[Row] | None:
        subq = (
            select(
                QuizAttempt.user_id, func.max(QuizAttempt.created_at).label("max_date")
            )
            .where(QuizAttempt.company_id == company_id)
            .group_by(QuizAttempt.user_id)
        ).subquery()

        stmt = (
            select(
                QuizAttempt.user_id,
                User.name.label("user_name"),
                QuizAttempt.created_at.label("last_attempt_at"),
            )
            .join(User, QuizAttempt.user_id == User.id)
            .join(
                subq,
                (QuizAttempt.user_id == subq.c.user_id)
                & (QuizAttempt.created_at == subq.c.max_date),
            )
            .where(QuizAttempt.company_id == company_id)
        )

        result = await self.session.execute(stmt)
        return result.all()
