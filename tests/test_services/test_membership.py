import pytest
from app.schemas.membership import MembershipCreateRequest, MembershipUpdateRequest
from app.services.membership import MembershipService
from app.models.enums import Roles
from tests.fixtures import test_user, test_second_user, test_company

service = MembershipService()


@pytest.mark.asyncio
class TestMembershipService:
    async def test_create_membership(self, uow, test_company, test_user):
        data = MembershipCreateRequest(
            company_id=test_company.id, user_id=test_user.id, role=Roles.MEMBER
        )
        membership = await service.create_membership(
            uow, data, current_user_id=test_user.id
        )
        await uow.commit()

        assert membership.user_id == test_user.id
        assert membership.company_id == test_company.id
        assert membership.role == Roles.MEMBER
        assert membership.is_active is True

    async def test_get_user_memberships(self, uow, test_user, test_company):
        data = MembershipCreateRequest(
            company_id=test_company.id, user_id=test_user.id, role=Roles.MEMBER
        )
        await service.create_membership(uow, data, current_user_id=test_user.id)

        memberships = await service.get_user_memberships(uow, user_id=test_user.id)
        assert isinstance(memberships.memberships, list)
        for m in memberships.memberships:
            assert m.user_id == test_user.id

    async def test_get_company_members(self, uow, test_company, test_user):
        data = MembershipCreateRequest(
            company_id=test_company.id, user_id=test_user.id, role=Roles.MEMBER
        )
        await service.create_membership(uow, data, current_user_id=test_user.id)

        members = await service.get_company_members(uow, company_id=test_company.id)
        assert len(members.memberships) == 2
        assert members.memberships[0].company_id == test_company.id

    async def test_update_membership(self, uow, test_company, test_user):
        data = MembershipCreateRequest(
            company_id=test_company.id, user_id=test_user.id, role=Roles.MEMBER
        )
        membership = await service.create_membership(
            uow, data, current_user_id=test_user.id
        )

        update_data = MembershipUpdateRequest(role=Roles.OWNER)
        updated_membership = await service.update_membership(
            uow,
            membership_id=membership.id,
            current_user_id=test_user.id,
            data=update_data,
        )

        assert updated_membership.role == Roles.OWNER

    async def test_delete_membership(self, uow, test_company, test_user):
        data = MembershipCreateRequest(
            company_id=test_company.id, user_id=test_user.id, role=Roles.MEMBER
        )
        membership = await service.create_membership(
            uow, data, current_user_id=test_user.id
        )

        deleted_membership = await service.delete_membership(
            uow, membership_id=membership.id, current_user_id=test_user.id
        )

        assert deleted_membership.is_active is False
        assert deleted_membership.left_at is not None

    async def test_cancel_membership(
        self, uow, test_company, test_user, test_second_user
    ):
        data = MembershipCreateRequest(
            company_id=test_company.id, user_id=test_second_user.id, role=Roles.MEMBER
        )
        membership = await service.create_membership(
            uow, data, current_user_id=test_user.id
        )

        canceled_membership = await service.cancel_membership(
            uow, membership_id=membership.id, current_user_id=test_second_user.id
        )

        assert canceled_membership.is_active is False
        assert canceled_membership.left_at is not None
