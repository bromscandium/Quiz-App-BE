from uuid import uuid4

import pytest

from app.enums.action_types import ActionTypes
from app.enums.action_statuses import ActionStatuses
from app.exceptions.base import InternalErrorException
from app.exceptions.company_actions import (
    CompanyActionNotFound,
    NotAllowedChangeCompanyAction,
    NotProvidedInfoForInvitation,
)
from app.exceptions.user import UnauthorizedUserAction
from app.schemas.company_actions import CompanyActionCreate, CompanyActionUpdate
from app.services.company_actions import CompanyActionsService
from tests.fixtures import test_company, test_second_user, test_user

service = CompanyActionsService()


@pytest.mark.asyncio
class TestCompanyActionsService:
    async def test_create_invitation_success(
        self, uow, test_user, test_second_user, test_company
    ):
        data = CompanyActionCreate(
            company_id=test_company.id,
            user_id=test_second_user.id,
            action_type=ActionTypes.INVITATION,
        )
        action = await service.create_company_action(uow, test_user.id, data)

        assert action.id is not None
        assert action.user.id == test_second_user.id
        assert action.company.id == test_company.id
        assert action.status == ActionStatuses.PENDING
        assert action.action_type == ActionTypes.INVITATION

    async def test_read_company_action_success(
        self, uow, test_user, test_second_user, test_company
    ):
        data = CompanyActionCreate(
            company_id=test_company.id,
            user_id=test_second_user.id,
            action_type=ActionTypes.INVITATION,
        )
        action = await service.create_company_action(uow, test_user.id, data)

        fetched = await service.read_company_action_by_id(uow, test_user.id, action.id)
        assert fetched.id == action.id

    async def test_read_company_action_unauthorized(
        self, uow, test_user, test_second_user, test_company
    ):
        data = CompanyActionCreate(
            company_id=test_company.id,
            user_id=test_second_user.id,
            action_type=ActionTypes.INVITATION,
        )
        action = await service.create_company_action(uow, test_user.id, data)

        other_user_id = uuid4()
        with pytest.raises(InternalErrorException):
            await service.read_company_action_by_id(uow, other_user_id, action.id)

    async def test_update_company_action_accept(
        self, uow, test_user, test_second_user, test_company
    ):
        data = CompanyActionCreate(
            company_id=test_company.id,
            user_id=test_second_user.id,
            action_type=ActionTypes.REQUEST,
        )
        action = await service.create_company_action(uow, test_second_user.id, data)

        update_data = CompanyActionUpdate(status=ActionStatuses.ACCEPTED)
        updated = await service.update_company_action(
            uow, test_user.id, action.id, update_data
        )

        assert updated.status == ActionStatuses.ACCEPTED

    async def test_update_company_action_not_allowed(
        self, uow, test_user, test_second_user, test_company
    ):
        data = CompanyActionCreate(
            company_id=test_company.id,
            user_id=test_second_user.id,
            action_type=ActionTypes.REQUEST,
        )
        action = await service.create_company_action(uow, test_second_user.id, data)

        update_data = CompanyActionUpdate(status=ActionStatuses.ACCEPTED)
        with pytest.raises(InternalErrorException):
            await service.update_company_action(
                uow, test_second_user.id, action.id, update_data
            )

    async def test_delete_company_action_success(
        self, uow, test_user, test_second_user, test_company
    ):
        data = CompanyActionCreate(
            company_id=test_company.id,
            user_id=test_second_user.id,
            action_type=ActionTypes.REQUEST,
        )
        action = await service.create_company_action(uow, test_second_user.id, data)

        await service.delete_company_action(uow, test_second_user.id, action.id)

        with pytest.raises(CompanyActionNotFound):
            await service.read_company_action_by_id(uow, test_second_user.id, action.id)
