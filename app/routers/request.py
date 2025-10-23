from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from app.dependencies.auth import get_auth_user_from_token
from app.dependencies.uow import get_uow
from app.schemas.request import (
    RequestDetailResponse,
    RequestSchema,
    RequestsListResponse,
    RequestUpdateRequest,
)
from app.services.request import RequestService
from app.unit_of_work.uow import UnitOfWork

request_service = RequestService()
router = APIRouter(prefix="/requests", tags=["requests"])


@router.post(
    "/", response_model=RequestDetailResponse, status_code=status.HTTP_201_CREATED
)
async def sent_request(
    data: RequestSchema,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> RequestDetailResponse:
    return await request_service.send_request(uow, data, current_user_id)


@router.put(
    "/update", response_model=RequestDetailResponse, status_code=status.HTTP_201_CREATED
)
async def update_request(
    data: RequestUpdateRequest,
    request_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> RequestDetailResponse:
    return await request_service.update_request(uow, current_user_id, request_id, data)


@router.get(
    "/company", response_model=RequestsListResponse, status_code=status.HTTP_201_CREATED
)
async def get_company_requests(
    company_id: UUID,
    offset: int = 0,
    limit: int = 20,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> RequestsListResponse:
    return await request_service.get_company_requests(
        uow, current_user_id, company_id, offset, limit
    )


@router.get(
    "/user", response_model=RequestsListResponse, status_code=status.HTTP_201_CREATED
)
async def get_user_requests(
    offset: int = 0,
    limit: int = 20,
    uow: UnitOfWork = Depends(get_uow),
    current_user_id=Depends(get_auth_user_from_token),
) -> RequestsListResponse:
    return await request_service.get_user_requests(uow, current_user_id, offset, limit)
