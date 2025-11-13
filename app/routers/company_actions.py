from uuid import UUID

from fastapi import APIRouter, Query
from fastapi.params import Depends
from starlette import status

from app.dependencies import get_auth_user_from_token, get_uow
from app.enums import ActionTypes, ActionStatuses
from app.schemas.company_actions import (
    CompanyActionCreate,
    CompanyActionSchema,
    CompanyActionsList,
    CompanyActionUpdate,
)
from app.services import CompanyActionsService
from app.unit_of_work import UnitOfWork

company_actions_service = CompanyActionsService()

router = APIRouter(prefix="/company_actions", tags=["company_actions"])


@router.post(
    "/", response_model=CompanyActionSchema, status_code=status.HTTP_201_CREATED
)
async def create_company_action(
    data: CompanyActionCreate,
    current_user_id: UUID = Depends(get_auth_user_from_token),
    uow: UnitOfWork = Depends(get_uow),
) -> CompanyActionSchema:
    return await company_actions_service.create_company_action(
        uow, current_user_id, data
    )


@router.get("/", response_model=CompanyActionsList)
async def read_company_actions(
    action_type: ActionTypes | None = Query(None),
    company_id: UUID | None = Query(None),
    status: ActionStatuses | None = Query(None),
    offset: int = 0,
    limit: int = 20,
    current_user_id: UUID = Depends(get_auth_user_from_token),
    uow: UnitOfWork = Depends(get_uow),
) -> CompanyActionsList:
    return await company_actions_service.read_company_actions(
        uow=uow,
        current_user_id=current_user_id,
        action_type=action_type,
        company_id=company_id,
        status=status,
        offset=offset,
        limit=limit,
    )


@router.get("/{company_action_id}", response_model=CompanyActionSchema)
async def read_company_action_by_id(
    company_action_id: UUID,
    current_user_id: UUID = Depends(get_auth_user_from_token),
    uow: UnitOfWork = Depends(get_uow),
) -> CompanyActionSchema:
    return await company_actions_service.read_company_action_by_id(
        uow=uow, current_user_id=current_user_id, company_action_id=company_action_id
    )


@router.put("/{company_action_id}", response_model=CompanyActionSchema)
async def update_company_action(
    company_action_id: UUID,
    data: CompanyActionUpdate,
    current_user_id: UUID = Depends(get_auth_user_from_token),
    uow: UnitOfWork = Depends(get_uow),
) -> CompanyActionSchema:
    return await company_actions_service.update_company_action(
        uow=uow,
        current_user_id=current_user_id,
        company_action_id=company_action_id,
        data=data,
    )


@router.delete("/{company_action_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_action(
    company_action_id: UUID,
    current_user_id: UUID = Depends(get_auth_user_from_token),
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    await company_actions_service.delete_company_action(
        uow=uow, current_user_id=current_user_id, company_action_id=company_action_id
    )
