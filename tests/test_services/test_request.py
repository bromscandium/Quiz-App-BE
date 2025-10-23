from datetime import datetime

import pytest

from app.exceptions.request import PrivateCompanyExceptionForRequest
from app.models.enums import Statuses
from app.schemas.request import RequestSchema, RequestUpdateRequest
from app.services.request import RequestService
from tests.fixtures import test_user, test_second_user, test_company

service = RequestService()


@pytest.mark.asyncio
class TestRequestService:
    async def test_send_request(self, uow, test_user, test_second_user, test_company):
        data = RequestSchema(
            company_id=test_company.id,
            user_id=test_second_user.id,
        )
        request = await service.send_request(uow, data, test_second_user.id)

        assert request.company_id == test_company.id
        assert request.user_id == test_second_user.id
        assert request.status == Statuses.PENDING

    async def test_update_request(self, uow, test_user, test_second_user, test_company):
        data = RequestSchema(
            company_id=test_company.id,
            user_id=test_second_user.id,
        )
        request = await service.send_request(uow, data, test_second_user.id)
        update_data = RequestUpdateRequest(
            status=Statuses.ACCEPTED,
            decision_time=datetime.now(),
            company_id=test_company.id,
            user_id=test_second_user.id,
        )
        updated_req = await service.update_request(
            uow, test_user.id, request.id, update_data
        )

        assert updated_req.status == Statuses.ACCEPTED

    async def test_get_user_requests(self, uow, test_second_user, test_company):
        data = RequestSchema(
            company_id=test_company.id,
            user_id=test_second_user.id,
        )
        await service.send_request(uow, data, test_second_user.id)

        response = await service.get_user_requests(uow, test_second_user.id)
        assert len(response.requests) >= 1
        for r in response.requests:
            assert r.user_id == test_second_user.id

    async def test_get_company_requests(
        self, uow, test_user, test_second_user, test_company
    ):
        data = RequestSchema(
            company_id=test_company.id,
            user_id=test_second_user.id,
        )
        await service.send_request(uow, data, test_second_user.id)

        response = await service.get_company_requests(
            uow, test_user.id, test_company.id
        )
        assert len(response.requests) >= 1
        for r in response.requests:
            assert r.company_id == test_company.id

    async def test_send_request_private_company(
        self, uow, test_second_user, test_company
    ):
        test_company.visibility = False
        await uow.company.update_by("id", test_company.id, visibility=False)

        data = RequestSchema(
            company_id=test_company.id,
            user_id=test_second_user.id,
        )

        with pytest.raises(PrivateCompanyExceptionForRequest):
            await service.send_request(uow, data, test_second_user.id)
