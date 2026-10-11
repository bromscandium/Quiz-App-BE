from datetime import datetime
from uuid import UUID

from fastapi import Depends, APIRouter

from app.dependencies import get_uow, get_auth_user_from_cookie
from app.schemas.stats import (
    UserStats,
    UserStatsQuizzesList,
    UserLastAttemptsList,
    CompanyUserQuizStatsList,
    CompanyUserLastAttemptsList,
    CompanyUserStatsList,
)
from app.services import StatsService
from app.unit_of_work import UnitOfWork

router = APIRouter(prefix="/stats", tags=["stats"])
service = StatsService()


@router.get("/user", response_model=UserStats)
async def read_user_stats(
        user_id: UUID,
        uow: UnitOfWork = Depends(get_uow),

        company_id: UUID | None = None,
        quiz_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
) -> UserStats:
    return await service.read_user_stats(
        uow,
        user_id,
        quiz_id,
        company_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/user/quizzes", response_model=UserStatsQuizzesList)
async def read_user_stats_quizzes(
        uow: UnitOfWork = Depends(get_uow),
        current_user_id: UUID = Depends(get_auth_user_from_cookie),
        company_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
) -> UserStatsQuizzesList:
    return await service.read_user_stats_quizzes(
        uow,
        current_user_id,
        company_id=company_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/user/quizzes/last-attempts", response_model=UserLastAttemptsList)
async def read_user_stats_last_attempts(
        uow: UnitOfWork = Depends(get_uow),
        current_user_id: UUID = Depends(get_auth_user_from_cookie),
        company_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
) -> UserLastAttemptsList:
    return await service.read_user_stats_last_attempts(
        uow,
        current_user_id,
        company_id=company_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/company/{company_id}/users", response_model=CompanyUserStatsList | None)
async def read_company_users_stats(
        company_id: UUID,
        uow: UnitOfWork = Depends(get_uow),
        current_user_id: UUID = Depends(get_auth_user_from_cookie),
        start_date: datetime | None = None,
        end_date: datetime | None = None,
) -> CompanyUserStatsList | None:
    return await service.read_company_users_stats(
        uow, current_user_id, company_id, start_date, end_date
    )


@router.get(
    "/company/{company_id}/user/{user_id}/quizzes",
    response_model=CompanyUserQuizStatsList | None,
)
async def read_company_user_quizzes_stats(
        company_id: UUID,
        user_id: UUID,
        uow: UnitOfWork = Depends(get_uow),
        current_user_id: UUID = Depends(get_auth_user_from_cookie),
        start_date: datetime | None = None,
        end_date: datetime | None = None,
) -> CompanyUserQuizStatsList | None:
    return await service.read_company_user_quizzes_stats(
        uow, current_user_id, company_id, user_id, start_date, end_date
    )


@router.get(
    "/company/{company_id}/last-attempts", response_model=CompanyUserLastAttemptsList | None
)
async def read_company_users_last_attempts(
        company_id: UUID,
        uow: UnitOfWork = Depends(get_uow),
        current_user_id: UUID = Depends(get_auth_user_from_cookie),
) -> CompanyUserLastAttemptsList | None:
    return await service.read_company_users_last_attempts(
        uow, current_user_id, company_id
    )
