from fastapi import APIRouter, Depends, status
from uuid import UUID

from app.dependencies.auth_token import get_auth_user_from_token
from app.unit_of_work.uow import UnitOfWork
from app.dependencies.uow import get_uow
from app.services.quiz_attempt import QuizAttemptService
from app.schemas.quiz_attempt import (
    QuizAttemptCreate,
    QuizAttemptSchema,
    QuizAttemptsList,
    UserStats,
)

router = APIRouter(prefix="/quiz_attempts", tags=["quiz_attempts"])
service = QuizAttemptService()


@router.post("/", response_model=QuizAttemptSchema, status_code=status.HTTP_201_CREATED)
async def create_quiz_attempt(
    data: QuizAttemptCreate,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id: UUID = Depends(get_auth_user_from_token),
) -> QuizAttemptSchema:
    return await service.create_quiz_attempt(uow, data, current_user_id)


@router.get("/{quiz_attempt_id}", response_model=QuizAttemptSchema)
async def read_quiz_attempt(
    quiz_attempt_id: UUID, uow: UnitOfWork = Depends(get_uow)
) -> QuizAttemptSchema:
    return await service.read_quiz_attempt_by_id(uow, quiz_attempt_id)


@router.get("/user/", response_model=QuizAttemptsList)
async def read_users_quiz_attempts(
    uow: UnitOfWork = Depends(get_uow),
    current_user_id: UUID = Depends(get_auth_user_from_token),
    offset: int = 0,
    limit: int = 20,
) -> QuizAttemptsList:
    return await service.read_users_quiz_attempts(uow, current_user_id, offset, limit)


@router.get("/user/stats", response_model=UserStats)
async def read_user_stats(
    uow: UnitOfWork = Depends(get_uow),
    current_user_id: UUID = Depends(get_auth_user_from_token),
    company_id: UUID | None = None,
    quiz_id: UUID | None = None,
) -> UserStats:
    return await service.read_user_stats(uow, current_user_id, quiz_id, company_id)


@router.delete("/delete/{quiz_attempt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_attempt(
    quiz_attempt_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id: UUID = Depends(get_auth_user_from_token),
) -> None:
    await service.delete_user_attempt(uow, quiz_attempt_id, current_user_id)
