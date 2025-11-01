from datetime import datetime
from uuid import UUID

from sqlalchemy import Row, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quiz_attempt import QuizAttempt


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
