from fastapi import APIRouter, Depends
from uuid import UUID
from fastapi import Query
from starlette import status

from app.dependencies.auth import get_auth_user_from_token
from app.dependencies.uow import get_uow
from app.schemas.membership import (
    MembershipCreateRequest,
    MembershipUpdateRequest,
    MembershipDetailResponse,
    MembershipListResponse,
)
from app.unit_of_work.uow import UnitOfWork
from app.services.membership import MembershipService

membership_service = MembershipService()
router = APIRouter(prefix="/memberships", tags=["memberships"])


@router.post(
    "/", response_model=MembershipDetailResponse, status_code=status.HTTP_201_CREATED
)
async def create_membership(
    data: MembershipCreateRequest,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> MembershipDetailResponse:
    return await membership_service.create_membership(uow, data, current_user_id)


@router.get(
    "/{membership_id}",
    response_model=MembershipDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def get_membership_by_id(
    membership_id: UUID, uow: UnitOfWork = Depends(get_uow)
) -> MembershipDetailResponse:
    return await membership_service.get_membership_by_id(uow, membership_id)


@router.get(
    "/user/{user_id}",
    response_model=MembershipListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user_memberships(
    user_id: UUID,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1),
    uow: UnitOfWork = Depends(get_uow),
) -> MembershipListResponse:
    return await membership_service.get_user_memberships(uow, user_id, offset, limit)


@router.get(
    "/company/{company_id}",
    response_model=MembershipListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_company_members(
    company_id: UUID,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1),
    uow: UnitOfWork = Depends(get_uow),
) -> MembershipListResponse:
    return await membership_service.get_company_members(uow, company_id, offset, limit)


@router.put(
    "/update/{membership_id}",
    response_model=MembershipDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def update_membership(
    membership_id: UUID,
    data: MembershipUpdateRequest,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> MembershipDetailResponse:
    return await membership_service.update_membership(
        uow, membership_id, current_user_id, data
    )


@router.put(
    "/{delete/membership_id}",
    response_model=MembershipDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_membership(
    membership_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> MembershipDetailResponse:
    return await membership_service.delete_membership(
        uow, membership_id, current_user_id
    )


@router.put(
    "/cancel/{membership_id}",
    response_model=MembershipDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def cancel_membership(
    membership_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> MembershipDetailResponse:
    return await membership_service.cancel_membership(
        uow, membership_id, current_user_id
    )
