from datetime import datetime
from uuid import UUID

from app.schemas.stats import UserStats
from app.unit_of_work import UnitOfWork


class StatsService:
    async def read_user_stats(
        self,
        uow: UnitOfWork,
        user_id: UUID,
        quiz_id: UUID | None = None,
        company_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> UserStats:
        result = await uow.stats.calculate_stats(
            user_id=user_id,
            quiz_id=quiz_id,
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
        )

        average_score = (
            round((result.total_correct or 0) / (result.total_questions or 1) * 100, 2)
            if result
            else 0.0
        )

        return UserStats(
            user_id=user_id,
            company_id=company_id,
            total_correct_answers=(result.total_correct or 0) if result else 0,
            total_answered_questions=(result.total_questions or 0) if result else 0,
            average_score=(average_score or 0) if result else 0,
            last_attempt_at=result.last_attempt if result else None,
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None,
        )
