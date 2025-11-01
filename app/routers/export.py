from fastapi import APIRouter, Depends
from app.dependencies import get_auth_user_from_token, get_uow
from app.enums.export_type import ExportType
from app.services import ExportService
from uuid import UUID

from app.unit_of_work import UnitOfWork

router = APIRouter(prefix="/export", tags=["export"])
service = ExportService()


@router.get("/quiz_results")
async def export_quiz_results(
    company_id: UUID,
    quiz_id: UUID,
    export_type: ExportType,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id: UUID = Depends(get_auth_user_from_token),
):
    return await service.export_quiz_results(
        uow=uow,
        current_user_id=current_user_id,
        company_id=company_id,
        quiz_id=quiz_id,
        export_type=export_type.value,
    )
