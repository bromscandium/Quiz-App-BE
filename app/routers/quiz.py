from fastapi import APIRouter, Depends, status
from uuid import UUID

from app.unit_of_work.uow import UnitOfWork
from app.services.quiz import QuizService
from app.schemas.quiz import QuizSchema, QuizCreate, QuizUpdate, QuizList
from app.schemas.question import QuestionsListCreate
from app.dependencies.uow import get_uow
from app.dependencies.auth_token import get_auth_user_from_token

router = APIRouter(prefix="/quizzes", tags=["quizzes"])
quiz_service = QuizService()


@router.post("/", response_model=QuizSchema, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    data: QuizCreate,
    questions_data: QuestionsListCreate,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id: UUID = Depends(get_auth_user_from_token),
) -> QuizSchema:
    return await quiz_service.create_quiz(uow, data, questions_data, current_user_id)


@router.get("/id/{quiz_id}", response_model=QuizSchema, status_code=status.HTTP_200_OK)
async def read_quiz(
    quiz_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id: UUID = Depends(get_auth_user_from_token),
) -> QuizSchema:
    return await quiz_service.read_quiz_by_id(uow, quiz_id, current_user_id)


@router.get(
    "/company/{company_id}", response_model=QuizList, status_code=status.HTTP_200_OK
)
async def read_company_quizzes(
    company_id: UUID,
    offset: int = 0,
    limit: int = 20,
    uow: UnitOfWork = Depends(get_uow),
) -> QuizList:
    return await quiz_service.read_company_quizzes(uow, company_id, offset, limit)


@router.put(
    "/update/{quiz_id}", response_model=QuizSchema, status_code=status.HTTP_200_OK
)
async def update_quiz(
    quiz_id: UUID,
    data: QuizUpdate,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id: UUID = Depends(get_auth_user_from_token),
) -> QuizSchema:
    return await quiz_service.update_quiz(uow, quiz_id, data, current_user_id)


@router.delete("/delete/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id: UUID = Depends(get_auth_user_from_token),
) -> None:
    return await quiz_service.delete_quiz(uow, quiz_id, current_user_id)
