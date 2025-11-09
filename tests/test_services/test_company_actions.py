from app.enums import ActionTypes, ActionStatuses
from tests.factories.company_actions import (
    CompanyActionCreateFactory,
    CompanyActionUpdateFactory,
)
from app.exceptions import (
    PrivateCompany,
)
from tests.fixtures import *


@pytest.mark.asyncio
async def test_create_request_action(uow, company_actions_service, company_1, user_3):
    request_data = CompanyActionCreateFactory.build(
        company_id=company_1.id,
        user_id=user_3.id,
        action_type=ActionTypes.REQUEST,
        status=ActionStatuses.PENDING,
    )
    action = await company_actions_service.create_company_action(
        uow, current_user_id=user_3.id, data=request_data
    )
    assert action.action_type == ActionTypes.REQUEST
    assert action.status == ActionStatuses.PENDING


@pytest.mark.asyncio
async def test_create_request_action_to_private(
    uow, company_actions_service, company_2, user_3
):
    request_data = CompanyActionCreateFactory.build(
        company_id=company_2.id,
        user_id=user_3.id,
        action_type=ActionTypes.REQUEST,
        status=ActionStatuses.PENDING,
    )
    with pytest.raises(PrivateCompany):
        await company_actions_service.create_company_action(
            uow, current_user_id=user_3.id, data=request_data
        )


@pytest.mark.asyncio
async def test_create_invitation_action(
    uow, company_actions_service, company_1, user_1, user_3
):
    invitation_data = CompanyActionCreateFactory.build(
        company_id=company_1.id,
        user_id=user_3.id,
        action_type=ActionTypes.INVITATION,
        status=ActionStatuses.PENDING,
    )
    action = await company_actions_service.create_company_action(
        uow, current_user_id=user_1.id, data=invitation_data
    )
    assert action.action_type == ActionTypes.INVITATION
    assert action.status == ActionStatuses.PENDING


@pytest.mark.asyncio
async def test_read_company_actions(uow, company_actions_service, company_1, user_3):
    request_data = CompanyActionCreateFactory.build(
        company_id=company_1.id,
        user_id=user_3.id,
        action_type=ActionTypes.REQUEST,
        status=ActionStatuses.PENDING,
    )
    action = await company_actions_service.create_company_action(
        uow, current_user_id=user_3.id, data=request_data
    )

    read_action = await company_actions_service.read_company_action_by_id(
        uow, current_user_id=user_3.id, company_action_id=action.id
    )
    assert read_action.id == action.id


@pytest.mark.asyncio
async def test_update_company_action(
    uow, company_actions_service, company_1, user_1, user_3
):
    invitation_data = CompanyActionCreateFactory.build(
        company_id=company_1.id,
        user_id=user_3.id,
        action_type=ActionTypes.INVITATION,
        status=ActionStatuses.PENDING,
    )
    action = await company_actions_service.create_company_action(
        uow, current_user_id=user_1.id, data=invitation_data
    )

    update_data = CompanyActionUpdateFactory.build(status=ActionStatuses.ACCEPTED)
    updated_action = await company_actions_service.update_company_action(
        uow, current_user_id=user_1.id, company_action_id=action.id, data=update_data
    )
    assert updated_action.status == ActionStatuses.ACCEPTED


@pytest.mark.asyncio
async def test_delete_company_action(
    uow, company_actions_service, company_1, user_1, user_3
):
    invitation_data = CompanyActionCreateFactory.build(
        company_id=company_1.id,
        user_id=user_3.id,
        action_type=ActionTypes.INVITATION,
        status=ActionStatuses.PENDING,
    )
    action = await company_actions_service.create_company_action(
        uow, current_user_id=user_1.id, data=invitation_data
    )

    deleted = await company_actions_service.delete_company_action(
        uow, current_user_id=user_1.id, company_action_id=action.id
    )

    assert deleted is None
