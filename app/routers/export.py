from fastapi import APIRouter, Depends, Query
from app.dependencies import get_auth_user_from_cookie, get_uow
from app.enums.export_type import ExportType
from app.services import ExportService
from uuid import UUID
from app.unit_of_work import UnitOfWork

router = APIRouter(prefix="/export", tags=["export"])
service = ExportService()


@router.get("/my-results")
async def export_my_results(
    quiz_id: UUID | None = Query(default=None),
    export_type: ExportType = Query(...),
    uow: UnitOfWork = Depends(get_uow),
    current_user_id: UUID = Depends(get_auth_user_from_cookie),
):
    return await service.export_user_results(
        uow=uow,
        user_id=current_user_id,
        quiz_id=quiz_id,
        export_type=export_type.value,
    )


@router.get("/company/{company_id}/user/{user_id}")
async def export_company_user_results(
    company_id: UUID,
    user_id: UUID,
    quiz_id: UUID | None = Query(default=None),
    export_type: ExportType = Query(...),
    uow: UnitOfWork = Depends(get_uow),
    current_user_id: UUID = Depends(get_auth_user_from_cookie),
):
    return await service.export_company_user_results(
        uow=uow,
        current_user_id=current_user_id,
        company_id=company_id,
        user_id=user_id,
        quiz_id=quiz_id,
        export_type=export_type.value,
    )


@router.get("/company/{company_id}/all-users")
async def export_company_all_users_results(
    company_id: UUID,
    quiz_id: UUID | None = Query(default=None),
    export_type: ExportType = Query(...),
    uow: UnitOfWork = Depends(get_uow),
    current_user_id: UUID = Depends(get_auth_user_from_cookie),
):
    return await service.export_company_all_results(
        uow=uow,
        current_user_id=current_user_id,
        company_id=company_id,
        quiz_id=quiz_id,
        export_type=export_type.value,
    )


@router.get("/company/{company_id}/quiz/{quiz_id}")
async def export_company_quiz_results(
    company_id: UUID,
    quiz_id: UUID,
    export_type: ExportType = Query(...),
    uow: UnitOfWork = Depends(get_uow),
    current_user_id: UUID = Depends(get_auth_user_from_cookie),
):
    return await service.export_company_quiz_results(
        uow=uow,
        current_user_id=current_user_id,
        company_id=company_id,
        quiz_id=quiz_id,
        export_type=export_type.value,
    )