import pytest

from app.schemas.membership import MembershipCreate, MembershipUpdate
from app.services.membership import MembershipService
from app.enums.roles import Roles
from tests.fixtures import test_user, test_second_user, test_company

service = MembershipService()


@pytest.mark.asyncio
class TestMembershipService:
    async def test_create_membership(self, uow, test_company, test_user):
        data = MembershipCreate(
            company_id=test_company.id, user_id=test_user.id, role=Roles.MEMBER
        )

        membership = await service.create_membership(uow, data)
        await uow.commit()

        assert getattr(membership, "role", None) == Roles.MEMBER
        assert getattr(membership, "is_active", None) is True

        if getattr(membership, "user", None) is not None:
            user_ok = getattr(membership.user, "id", None) == test_user.id
        else:
            user_ok = getattr(membership, "user_id", None) == test_user.id
        assert user_ok

        if getattr(membership, "company", None) is not None:
            company_ok = getattr(membership.company, "id", None) == test_company.id
        else:
            company_ok = getattr(membership, "company_id", None) == test_company.id
        assert company_ok

    async def test_read_user_memberships(self, uow, test_user, test_company):
        data = MembershipCreate(
            company_id=test_company.id, user_id=test_user.id, role=Roles.MEMBER
        )
        membership = await service.create_membership(uow, data)
        await uow.commit()

        m = await service.read_membership_by_id(uow, membership.id)
        assert m is not None

    async def test_read_company_members_and_roles_filter(
        self, uow, test_company, test_user, test_second_user
    ):
        m1 = MembershipCreate(
            company_id=test_company.id, user_id=test_user.id, role=Roles.OWNER
        )
        m2 = MembershipCreate(
            company_id=test_company.id, user_id=test_second_user.id, role=Roles.MEMBER
        )

        await service.create_membership(uow, m1)
        await service.create_membership(uow, m2)
        await uow.commit()

        all_members = await service.read_company_members(
            uow, current_user_id=test_user.id, company_id=test_company.id, roles=None
        )
        assert isinstance(all_members.memberships, list)
        assert len(all_members.memberships) >= 2

        owners = await service.read_company_members(
            uow,
            current_user_id=test_user.id,
            company_id=test_company.id,
            roles={Roles.OWNER},
        )
        assert all((m.role == Roles.OWNER) for m in owners.memberships)

    async def test_update_membership(
        self, uow, test_company, test_user, test_second_user
    ):
        data = MembershipCreate(
            company_id=test_company.id, user_id=test_second_user.id, role=Roles.MEMBER
        )
        membership = await service.create_membership(uow, data)
        await uow.commit()

        update = MembershipUpdate(role=Roles.ADMIN, is_active=True)
        updated = await service.update_membership(
            uow, membership_id=membership.id, data=update, current_user_id=test_user.id
        )
        await uow.commit()

        assert updated.role == Roles.ADMIN

    async def test_delete_membership(self, uow, test_company, test_user):
        data = MembershipCreate(
            company_id=test_company.id, user_id=test_user.id, role=Roles.MEMBER
        )
        membership = await service.create_membership(uow, data)

        await service.delete_membership(
            uow, membership_id=membership.id, current_user_id=test_user.id
        )

        items, _ = await uow.membership.read(
            field="id", value=membership.id, offset=0, limit=1
        )
        assert items == []
