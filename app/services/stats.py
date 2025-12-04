from datetime import datetime
from uuid import UUID

from app.enums import Roles
from app.exceptions import UnauthorizedQuizAction
from app.schemas.stats import (
    UserStats,
    UserQuizStats,
    UserLastAttempt,
    UserLastAttemptsList,
    UserStatsQuizzesList,
    CompanyUserStats,
    CompanyUserStatsList,
    CompanyUserQuizStats,
    CompanyUserQuizStatsList,
    CompanyUserLastAttempt,
    CompanyUserLastAttemptsList,
)
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

    async def read_user_stats_quizzes(
            self,
            uow: UnitOfWork,
            user_id: UUID,
            company_id: UUID | None = None,
            start_date: datetime | None = None,
            end_date: datetime | None = None,
    ) -> UserStatsQuizzesList:
        results = await uow.stats.calculate_user_quizzes_stats(
            user_id=user_id,
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
        )

        user_attempts = [
            UserQuizStats(
                quiz_id=row.quiz_id,
                quiz_title=row.quiz_title,
                average_score=round(row.average_score, 2) if row.average_score else 0.0,
                attempts_count=row.attempts_count or 0,
                last_attempt_at=row.last_attempt_at,
            )
            for row in results
        ]

        return UserStatsQuizzesList(user_attempts=user_attempts)

    async def read_user_stats_last_attempts(
            self,
            uow: UnitOfWork,
            user_id: UUID,
            company_id: UUID | None = None,
            start_date: datetime | None = None,
            end_date: datetime | None = None,
    ) -> UserLastAttemptsList:
        results = await uow.stats.get_user_last_attempts(
            user_id=user_id,
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
        )

        user_attempts = [
            UserLastAttempt(
                quiz_id=row.quiz_id,
                quiz_title=row.quiz_title,
                last_attempt_at=row.last_attempt_at,
            )
            for row in results
        ]

        return UserLastAttemptsList(user_attempts=user_attempts)

    async def _check_company_admin_access(
            self,
            uow: UnitOfWork,
            current_user_id: UUID,
            company_id: UUID,
    ) -> bool | None:
        memberships, _ = await uow.membership.read(
            field="user_id", value=current_user_id, offset=0, limit=100
        )

        if any(
                m.company_id == company_id
                and m.role in {Roles.ADMIN, Roles.OWNER}
                and m.is_active
                for m in memberships
        ):
            return False

        return True

    async def read_company_users_stats(
            self,
            uow: UnitOfWork,
            current_user_id: UUID,
            company_id: UUID,
            start_date: datetime | None = None,
            end_date: datetime | None = None,
    ) -> CompanyUserStatsList | None:
        if await self._check_company_admin_access(uow, current_user_id, company_id):
            return None

        results = await uow.stats.calculate_company_users_stats(
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
        )

        if not results:
            return CompanyUserStatsList(user_stats=[])

        user_stats = [
            CompanyUserStats(
                user_id=row.user_id,
                user_name=row.user_name,
                average_score=round(row.average_score, 2) if row.average_score else 0.0,
                total_attempts=row.total_attempts or 0,
                last_attempt_at=row.last_attempt_at,
            )
            for row in results
        ]

        return CompanyUserStatsList(user_stats=user_stats)

    async def read_company_user_quizzes_stats(
            self,
            uow: UnitOfWork,
            current_user_id: UUID,
            company_id: UUID,
            user_id: UUID,
            start_date: datetime | None = None,
            end_date: datetime | None = None,
    ) -> CompanyUserQuizStatsList | None:
        if await self._check_company_admin_access(uow, current_user_id, company_id):
            return None

        results = await uow.stats.calculate_company_user_quizzes_stats(
            company_id=company_id,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

        if not results:
            return CompanyUserQuizStatsList(quiz_stats=[])

        quiz_stats = [
            CompanyUserQuizStats(
                quiz_id=row.quiz_id,
                quiz_title=row.quiz_title,
                average_score=round(row.average_score, 2) if row.average_score else 0.0,
                attempts_count=row.attempts_count or 0,
                last_attempt_at=row.last_attempt_at,
            )
            for row in results
        ]

        return CompanyUserQuizStatsList(quiz_stats=quiz_stats)

    async def read_company_users_last_attempts(
            self,
            uow: UnitOfWork,
            current_user_id: UUID,
            company_id: UUID,
    ) -> CompanyUserLastAttemptsList | None:
        if await self._check_company_admin_access(uow, current_user_id, company_id):
            return None

        results = await uow.stats.get_company_users_last_attempts(
            company_id=company_id,
        )

        if not results:
            return CompanyUserLastAttemptsList(user_attempts=[])

        user_attempts = [
            CompanyUserLastAttempt(
                user_id=row.user_id,
                user_name=row.user_name,
                last_attempt_at=row.last_attempt_at,
            )
            for row in results
        ]

        return CompanyUserLastAttemptsList(user_attempts=user_attempts)
