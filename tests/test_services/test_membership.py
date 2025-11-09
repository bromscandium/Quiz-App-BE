from app.enums import Roles
from app.exceptions import (
    SetAnotherOwnerError,
)
from tests.factories.membership import MembershipCreateFactory, MembershipUpdateFactory
from tests.fixtures import *


@pytest.mark.asyncio
async def test_create_membership(uow, membership_service, user_3, company_1):
    create_data = MembershipCreateFactory.build(
        user_id=user_3.id, company_id=company_1.id
    )
    membership = await membership_service.create_membership(uow, create_data)

    assert membership.id is not None
    assert membership.user.id == user_3.id
    assert membership.company.id == company_1.id


@pytest.mark.asyncio
async def test_read_membership_by_id(uow, membership_service, user_3, company_1):
    create_data = MembershipCreateFactory.build(
        user_id=user_3.id, company_id=company_1.id
    )
    membership = await membership_service.create_membership(uow, create_data)

    result = await membership_service.read_membership_by_id(uow, membership.id)
    assert result.id == membership.id
    assert result.user.id == membership.user.id
    assert result.company.id == membership.company.id


@pytest.mark.asyncio
async def test_read_user_memberships(
    uow, membership_service, company_service, user_1, company_1_create
):
    await company_service.create_company(uow, user_1.id, company_1_create)
    result = await membership_service.read_user_memberships(uow, user_1.id)
    assert result.total >= 1


@pytest.mark.asyncio
async def test_read_company_members(uow, membership_service, user_1, company_1):
    result = await membership_service.read_company_members(uow, user_1.id, company_1.id)
    assert result.total >= 1


@pytest.mark.asyncio
async def test_update_membership(uow, membership_service, company_1, user_1, user_3):
    create_data = MembershipCreateFactory.build(
        user_id=user_3.id, company_id=company_1.id
    )
    membership = await membership_service.create_membership(uow, create_data)

    update_data = MembershipUpdateFactory.build(role=Roles.ADMIN, is_active=True)
    updated = await membership_service.update_membership(
        uow, membership.id, update_data, user_1.id
    )
    assert updated.id == membership.id
    assert updated.role == Roles.ADMIN


@pytest.mark.asyncio
async def test_update_membership_set_owner_error(
    uow, membership_service, user_3, company_1, user_1
):
    create_data = MembershipCreateFactory.build(
        user_id=user_3.id, company_id=company_1.id
    )
    membership = await membership_service.create_membership(uow, create_data)

    update_data = MembershipUpdateFactory.build(role=Roles.OWNER)
    with pytest.raises(SetAnotherOwnerError):
        await membership_service.update_membership(
            uow, membership.id, update_data, user_1.id
        )


@pytest.mark.asyncio
async def test_delete_membership(uow, membership_service, user_3, company_1, user_1):
    create_data = MembershipCreateFactory.build(
        user_id=user_3.id, company_id=company_1.id
    )
    membership = await membership_service.create_membership(uow, create_data)

    deleted = await membership_service.delete_membership(uow, membership.id, user_1.id)
    assert deleted is None
