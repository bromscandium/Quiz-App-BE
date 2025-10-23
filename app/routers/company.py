from fastapi import APIRouter, Depends, status
from uuid import UUID

from app.dependencies.auth import get_auth_user_from_token

from app.dependencies.uow import get_uow
from app.schemas.company import (
    CompanyDetailResponse,
    CompanyCreateRequest,
    CompaniesListResponse,
    CompanyUpdateRequest,
)
from app.services.company import CompanyService

from app.unit_of_work.uow import UnitOfWork

company_service = CompanyService()

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post(
    "/", response_model=CompanyDetailResponse, status_code=status.HTTP_201_CREATED
)
async def create_company(
    data: CompanyCreateRequest,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> CompanyDetailResponse:
    return await company_service.create_company(uow, current_user_id, data)


@router.get(
    "/{company_id}",
    response_model=CompanyDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def get_company_by_id(
    company_id: UUID, uow: UnitOfWork = Depends(get_uow)
) -> CompanyDetailResponse:
    return await company_service.get_company_by_id(uow, company_id)


@router.get("/", response_model=CompaniesListResponse, status_code=status.HTTP_200_OK)
async def read_all_companies(
    offset: int = 0, limit: int = 20, uow: UnitOfWork = Depends(get_uow)
) -> CompaniesListResponse:
    return await company_service.read_all_companies(uow, offset, limit)


@router.put(
    "/{company_id}",
    response_model=CompanyDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def update_company(
    company_id: UUID,
    data: CompanyUpdateRequest,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> CompanyDetailResponse:
    return await company_service.update_company(uow, company_id, current_user_id, data)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> None:
    await company_service.delete_company(uow, company_id, current_user_id)
