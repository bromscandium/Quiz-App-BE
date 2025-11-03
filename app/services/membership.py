from uuid import UUID

from app.enums import Roles
from app.exceptions import (
    MembershipNotFound,
    PrivateCompany,
    SetAnotherOwnerError,
    UnauthorizedCompanyOwner,
)
from app.permissions import *
from app.schemas.membership import (
    CompanyMembership,
    CompanyMembershipsList,
    MembershipCreate,
    MembershipSchema,
    MembershipUpdate,
    UserMembership,
    UserMembershipsList,
)

from app.unit_of_work import UnitOfWork
from app.utils import LoggerUtil


class MembershipService:
    def __init__(self):
        self.logger_util = LoggerUtil()

    async def create_membership(
        self,
        uow: UnitOfWork,
        data: MembershipCreate,
    ) -> MembershipSchema:
        membership = await uow.membership.create(**data.model_dump())
        await uow.session.flush()
        await uow.session.refresh(membership, attribute_names=["user", "company"])

        items, _ = await uow.membership.read(
            field="id",
            value=membership.id,
            offset=0,
            limit=1,
            load_relationships=["user", "company", "company.owner"],
            use_joined_load=False,
        )

        if items:
            membership = items[0]

        return MembershipSchema.model_validate(membership)

    async def read_membership_by_id(
        self, uow: UnitOfWork, value: UUID
    ) -> MembershipSchema | None:
        membership, _ = await uow.membership.read(
            field="id",
            value=value,
            offset=0,
            limit=1,
            load_relationships=["user", "company", "company.owner"],
        )

        if not membership:
            return None

        if not await check_company_visibility(membership[0].company.id, uow):
            self.logger_util.info("Company not found")
            raise PrivateCompany

        return MembershipSchema.model_validate(membership[0])

    async def read_user_memberships(
        self, uow: UnitOfWork, current_user_id: UUID, offset: int = 0, limit: int = 20
    ) -> UserMembershipsList:
        memberships, total = await uow.membership.read(
            field="user_id",
            value=current_user_id,
            offset=offset,
            limit=limit,
            load_relationships=["user", "company", "company.owner"],
        )

        active_total = [m for m in memberships if m.is_active]

        memberships = [UserMembership.model_validate(m) for m in memberships]
        return UserMembershipsList(
            memberships=memberships, total=total, active_total=len(active_total)
        )

    async def read_company_members(
        self,
        uow: UnitOfWork,
        current_user_id: UUID,
        company_id: UUID,
        offset: int = 0,
        limit: int = 20,
        roles: set[Roles] | None = None,
    ) -> CompanyMembershipsList | None:
        if not await check_owner_permission(current_user_id, uow, company_id):
            self.logger_util.info("Owner not athorized")
            raise UnauthorizedCompanyOwner

        if await check_company_visibility(company_id, uow):
            self.logger_util.info("Company is private")
            raise PrivateCompany

        memberships, total = await uow.membership.read(
            field="company_id",
            value=company_id,
            offset=offset,
            limit=limit,
            load_relationships=["user", "company"],
        )

        if roles is not None:
            memberships = [m for m in memberships if m.role in roles]

        active_items = [m for m in memberships if m.is_active]

        memberships = [CompanyMembership.model_validate(m) for m in memberships]
        return CompanyMembershipsList(
            memberships=memberships, total=total, active_total=len(active_items)
        )

    async def update_membership(
        self,
        uow: UnitOfWork,
        membership_id: UUID,
        data: MembershipUpdate,
        current_user_id: UUID,
    ) -> MembershipSchema:
        membership = await self.read_membership_by_id(uow, membership_id)

        if membership is None:
            self.logger_util.info("Membership not found")
            raise MembershipNotFound

        is_self_update = membership.user.id == current_user_id and membership.is_active

        if not is_self_update:
            await check_owner_permission(current_user_id, uow, membership.company.id)

        if data.role == Roles.OWNER:
            self.logger_util.info("There are no two owners")
            raise SetAnotherOwnerError

        update_data = data.model_dump(
            exclude_unset=True, exclude={"role"} if is_self_update else None
        )

        membership = await uow.membership.update_by("id", membership_id, **update_data)
        await uow.session.refresh(
            membership,
            attribute_names=["user", "company"],
        )

        membership = await self.read_membership_by_id(uow, membership_id)

        return MembershipSchema.model_validate(membership)

    async def delete_membership(
        self, uow: UnitOfWork, membership_id: UUID, current_user_id: UUID
    ) -> None:
        membership, _ = await uow.membership.read(
            field="id", value=membership_id, offset=0, limit=1
        )

        if not membership:
            self.logger_util.info("Membership not found")
            raise MembershipNotFound

        if not await check_owner_permission(
            current_user_id, uow, membership[0].company_id
        ):
            self.logger_util.info("Owner is not authorized")
            raise UnauthorizedCompanyOwner

        await uow.membership.delete_by("id", membership_id)
