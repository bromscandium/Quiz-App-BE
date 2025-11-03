from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette import status

from app.dependencies import get_auth_user_from_token, get_uow
from app.enums.roles import Roles
from app.schemas.membership import (
    CompanyMembershipsList,
    MembershipCreate,
    MembershipSchema,
    MembershipUpdate,
    UserMembershipsList,
)
from app.services import MembershipService
from app.unit_of_work import UnitOfWork

membership_service = MembershipService()
router = APIRouter(prefix="/memberships", tags=["memberships"])


@router.post("/", response_model=MembershipSchema, status_code=status.HTTP_201_CREATED)
async def create_membership(
    data: MembershipCreate,
    uow: UnitOfWork = Depends(get_uow),
) -> MembershipSchema:
    return await membership_service.create_membership(uow, data)


@router.get(
    "/id/{membership_id}",
    response_model=MembershipSchema,
    status_code=status.HTTP_200_OK,
)
async def read_membership_by_id(
    membership_id: UUID, uow: UnitOfWork = Depends(get_uow)
) -> MembershipSchema:
    return await membership_service.read_membership_by_id(uow, membership_id)


@router.get(
    "/user/{current_user_id}",
    response_model=UserMembershipsList,
    status_code=status.HTTP_200_OK,
)
async def read_user_memberships(
    current_user_id: UUID = Depends(get_auth_user_from_token),
    offset: int = 0,
    limit: int = 20,
    uow: UnitOfWork = Depends(get_uow),
) -> UserMembershipsList:
    return await membership_service.read_user_memberships(
        uow, current_user_id, offset, limit
    )


@router.get(
    "/company/{company_id}",
    response_model=CompanyMembershipsList,
    status_code=status.HTTP_200_OK,
)
async def read_company_members(
    company_id: UUID,
    offset: int = 0,
    limit: int = 20,
    roles: list[Roles] | None = Query(None),
    current_user_id: UUID = Depends(get_auth_user_from_token),
    uow: UnitOfWork = Depends(get_uow),
) -> CompanyMembershipsList:
    return await membership_service.read_company_members(
        uow=uow,
        current_user_id=current_user_id,
        company_id=company_id,
        offset=offset,
        limit=limit,
        roles=set(roles) if roles else None,
    )


@router.put(
    "/update/{membership_id}",
    response_model=MembershipSchema,
    status_code=status.HTTP_200_OK,
)
async def update_membership(
    membership_id: UUID,
    data: MembershipUpdate,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> MembershipSchema:
    return await membership_service.update_membership(
        uow, membership_id, data, current_user_id
    )


@router.delete(
    "/delete/{membership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_membership(
    membership_id: UUID,
    current_user_id: UUID = Depends(get_auth_user_from_token),
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    return await membership_service.delete_membership(
        uow, current_user_id=current_user_id, membership_id=membership_id
    )
