from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from app.dependencies.auth import get_auth_user_from_token
from app.dependencies.uow import get_uow
from app.schemas.invitation import (
    InvitationDetailResponse,
    InvitationSchema,
    InvitationListResponse,
    InvitationUpdateRequest,
)
from app.services.invitation import InvitationService
from app.unit_of_work.uow import UnitOfWork

invitation_service = InvitationService()
router = APIRouter(prefix="/invitations", tags=["invitations"])


@router.post(
    "/", response_model=InvitationDetailResponse, status_code=status.HTTP_201_CREATED
)
async def send_invitation(
    data: InvitationSchema,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> InvitationDetailResponse:
    return await invitation_service.send_invitation(uow, current_user_id, data)


@router.put(
    "/update",
    response_model=InvitationDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def update_invitation(
    data: InvitationUpdateRequest,
    request_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> InvitationDetailResponse:
    return await invitation_service.update_invitation(
        uow, current_user_id, request_id, data
    )


@router.get(
    "/company",
    response_model=InvitationListResponse,
    status_code=status.HTTP_201_CREATED,
)
async def get_company_invitations(
    company_id: UUID,
    offset: int = 0,
    limit: int = 20,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> InvitationListResponse:
    return await invitation_service.get_company_invitations(
        uow, current_user_id, company_id, offset, limit
    )


@router.get(
    "/user", response_model=InvitationListResponse, status_code=status.HTTP_201_CREATED
)
async def get_user_invitations(
    offset: int = 0,
    limit: int = 20,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> InvitationListResponse:
    return await invitation_service.get_user_invitations(
        uow, current_user_id, offset, limit
    )
