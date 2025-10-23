from uuid import UUID

from app.exceptions.request import (
    RequestInternalErrorException,
    RequestNotFound,
    PrivateCompanyExceptionForRequest,
    UnauthorizedRequestException,
)
from app.models.enums import Statuses
from app.permissions.company import check_company_visibility
from app.permissions.membership import check_owner_permission
from app.schemas.membership import MembershipCreateRequest
from app.schemas.request import (
    RequestDetailResponse,
    RequestsListResponse,
    RequestSchema,
    RequestUpdateRequest,
)

from app.services.user import UserService
from app.unit_of_work.uow import UnitOfWork
from app.utils.logger import logger


class RequestService:
    def __init__(self):
        self.user_service = UserService()

    async def send_request(
        self, uow: UnitOfWork, data: RequestSchema, current_user_id: UUID
    ) -> RequestDetailResponse:
        try:
            if not await check_company_visibility(company_id=data.company_id, uow=uow):
                raise PrivateCompanyExceptionForRequest
            if current_user_id != data.user_id:
                raise UnauthorizedRequestException
            request = await uow.request.create(**data.model_dump())
            await uow.session.flush()

            return RequestDetailResponse.model_validate(request)
        except PrivateCompanyExceptionForRequest:
            raise PrivateCompanyExceptionForRequest
        except UnauthorizedRequestException:
            raise UnauthorizedRequestException
        except Exception as e:
            logger.exception(f"Error while sending request: {e}")
            raise RequestInternalErrorException

    async def update_request(
        self,
        uow: UnitOfWork,
        current_user_id: UUID,
        request_id: UUID,
        data: RequestUpdateRequest,
    ) -> RequestDetailResponse:
        try:
            if data.status == Statuses.ACCEPTED or data.status == Statuses.DECLINED:
                await check_owner_permission(current_user_id, uow)

            request = await uow.request.update_by(
                "id", request_id, status=data.status, decision_time=data.decision_time
            )

            if not request:
                raise RequestNotFound
            await uow.session.flush()

            if data.status == Statuses.ACCEPTED:
                new_member_data = MembershipCreateRequest(
                    company_id=data.company_id,
                    user_id=data.user_id,
                )

                await uow.membership.create(**new_member_data.model_dump())
            return RequestDetailResponse.model_validate(request)
        except RequestNotFound:
            raise RequestNotFound
        except Exception as e:
            logger.exception(f"Error while cancelling request: {e}")
            raise RequestInternalErrorException

    async def get_company_requests(
        self,
        uow: UnitOfWork,
        current_user_id: UUID,
        company_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> RequestsListResponse:
        await check_owner_permission(current_user_id, uow)
        requests, total = await uow.request.read(
            "company_id", company_id, offset, limit
        )
        requests_details = [
            RequestDetailResponse.model_validate(request) for request in requests
        ]
        return RequestsListResponse(requests=requests_details, total=total)

    async def get_user_requests(
        self, uow: UnitOfWork, current_user_id: UUID, offset: int = 0, limit: int = 20
    ) -> RequestsListResponse:
        requests, total = await uow.request.read(
            "user_id", current_user_id, offset, limit
        )
        requests_details = [
            RequestDetailResponse.model_validate(request) for request in requests
        ]
        return RequestsListResponse(requests=requests_details, total=total)
