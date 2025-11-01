from uuid import UUID

from fastapi import Depends, APIRouter

from app.dependencies import get_uow, get_auth_user_from_token
from app.schemas.stats import UserStats
from app.services import StatsService
from app.unit_of_work import UnitOfWork

router = APIRouter(prefix="/stats", tags=["stats"])
service = StatsService()


@router.get("/user", response_model=UserStats)
async def read_user_stats(
    uow: UnitOfWork = Depends(get_uow),
    current_user_id: UUID = Depends(get_auth_user_from_token),
    company_id: UUID | None = None,
    quiz_id: UUID | None = None,
) -> UserStats:
    return await service.read_user_stats(uow, current_user_id, quiz_id, company_id)
