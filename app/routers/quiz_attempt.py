from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.dependencies import get_auth_user_from_token, get_uow
from app.schemas.quiz_attempt import (
    QuizAttemptCreate,
    QuizAttemptSchema,
    QuizAttemptsList,
)
from app.services import QuizAttemptService
from app.unit_of_work import UnitOfWork

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
async def read_quiz_attempt_by_id(
    quiz_attempt_id: UUID, user_id: UUID, uow: UnitOfWork = Depends(get_uow)
) -> QuizAttemptSchema:
    return await service.read_quiz_attempt_by_id(uow, user_id, quiz_attempt_id)


@router.get("/user/", response_model=QuizAttemptsList)
async def read_user_quiz_attempts(
    uow: UnitOfWork = Depends(get_uow),
    current_user_id: UUID = Depends(get_auth_user_from_token),
    offset: int = 0,
    limit: int = 20,
) -> QuizAttemptsList:
    return await service.read_users_quiz_attempts(uow, current_user_id, offset, limit)


@router.get("/company/", response_model=QuizAttemptsList)
async def read_company_quiz_attempts(
    company_id: UUID,
    quiz_id: UUID | None,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id: UUID = Depends(get_auth_user_from_token),
    offset: int = 0,
    limit: int = 20,
) -> QuizAttemptsList:
    return await service.read_company_quiz_attempts(
        uow=uow,
        current_user_id=current_user_id,
        company_id=company_id,
        quiz_id=quiz_id,
        offset=offset,
        limit=limit,
    )
