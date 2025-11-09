from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.dependencies import get_auth_user_from_token, get_uow
from app.schemas.company import (
    CompaniesList,
    CompanyCreate,
    CompanySchema,
    CompanyUpdate,
)
from app.services import CompanyService
from app.unit_of_work import UnitOfWork

company_service = CompanyService()

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/", response_model=CompanySchema, status_code=status.HTTP_201_CREATED)
async def create_company(
    data: CompanyCreate,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> CompanySchema:
    return await company_service.create_company(uow, current_user_id, data)


@router.get(
    "/id/{company_id}",
    response_model=CompanySchema,
    status_code=status.HTTP_200_OK,
)
async def read_company_by_id(
    company_id: UUID, uow: UnitOfWork = Depends(get_uow)
) -> CompanySchema:
    return await company_service.read_company_by_id(uow, company_id)


@router.get("/all", response_model=CompaniesList, status_code=status.HTTP_200_OK)
async def read_all_companies(
    offset: int = 0, limit: int = 20, uow: UnitOfWork = Depends(get_uow)
) -> CompaniesList:
    return await company_service.read_all_companies(uow, offset, limit)


@router.put(
    "/update/{company_id}",
    response_model=CompanySchema,
    status_code=status.HTTP_200_OK,
)
async def update_company(
    company_id: UUID,
    data: CompanyUpdate,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> CompanySchema:
    return await company_service.update_company(uow, company_id, data, current_user_id)


@router.delete("/delete/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> None:
    await company_service.delete_company(uow, company_id, current_user_id)
