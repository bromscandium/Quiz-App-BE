from uuid import UUID

from sqlalchemy import select, func, Row

from app.models.quiz_attempt import QuizAttempt
from app.unit_of_work.uow import UnitOfWork


class StatsUtil:
    async def calculate_stats(
        self, uow: UnitOfWork, user_id: UUID, quiz_id: UUID, company_id: UUID
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

        result = await uow.session.execute(stmt)
        return result.first()
