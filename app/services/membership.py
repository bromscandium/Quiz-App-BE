from uuid import UUID

from app.enums.roles import Roles
from app.exceptions.base import InternalErrorException
from app.exceptions.company import NotOwnerOfCompany
from app.exceptions.company_actions import PrivateCompany
from app.exceptions.membership import (
    MembershipNotFound,
    SetAnotherOwner,
)
from app.exceptions.user import UnauthorizedUserAction
from app.permissions.company import check_company_visibility
from app.permissions.ownership import check_owner_permission
from app.schemas.membership import (
    MembershipSchema,
    MembershipCreate,
    MembershipUpdate,
    UserMembershipsList,
    UserMembership,
    CompanyMembershipsList,
    CompanyMembership,
)

from app.unit_of_work.uow import UnitOfWork
from app.utils.logger import logger


class MembershipService:
    async def create_membership(
        self,
        uow: UnitOfWork,
        data: MembershipCreate,
    ) -> MembershipSchema:
        try:
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

        except Exception as e:
            logger.exception(f"Error while creating membership: {e}")
            raise InternalErrorException

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
            raise PrivateCompany

        return MembershipSchema.model_validate(membership[0])

    async def read_user_memberships(
        self, uow: UnitOfWork, current_user_id: UUID, offset: int = 0, limit: int = 20
    ) -> UserMembershipsList:
        items, total = await uow.membership.read(
            field="user_id",
            value=current_user_id,
            offset=offset,
            limit=limit,
            load_relationships=["user", "company"],
        )

        active_items = [m for m in items if m.is_active]
        active_total = len(active_items)

        memberships = [UserMembership.model_validate(m) for m in items]
        return UserMembershipsList(
            memberships=memberships, total=total, active_total=active_total
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
        try:
            if not await check_owner_permission(
                current_user_id, uow, company_id
            ) and await check_company_visibility(company_id, uow):
                raise PrivateCompany

            items, total = await uow.membership.read(
                field="company_id",
                value=company_id,
                offset=offset,
                limit=limit,
                load_relationships=["user", "company"],
            )

            if roles is not None:
                items = [m for m in items if m.role in roles]

            active_items = [m for m in items if m.is_active]
            active_total = len(active_items)

            memberships = [CompanyMembership.model_validate(m) for m in items]
            return CompanyMembershipsList(
                memberships=memberships, total=total, active_total=active_total
            )

        except PrivateCompany:
            raise

    async def update_membership(
        self,
        uow: UnitOfWork,
        membership_id: UUID,
        data: MembershipUpdate,
        current_user_id: UUID,
    ) -> MembershipSchema:
        try:
            membership = await self.read_membership_by_id(uow, membership_id)

            is_self_update = (
                membership.user.id == current_user_id and membership.is_active
            )

            if not is_self_update:
                await check_owner_permission(
                    current_user_id, uow, membership.company.id
                )

            if data.role == Roles.OWNER:
                raise SetAnotherOwner

            update_data = data.model_dump(
                exclude_unset=True, exclude={"role"} if is_self_update else None
            )

            membership = await uow.membership.update_by(
                "id", membership_id, **update_data
            )
            await uow.session.refresh(
                membership,
                attribute_names=[
                    "user",
                    "company",
                ],
            )

            membership = await self.read_membership_by_id(uow, membership_id)

            return MembershipSchema.model_validate(membership)
        except (UnauthorizedUserAction, MembershipNotFound, SetAnotherOwner):
            raise
        except Exception as e:
            logger.exception(f"Error while updating membership: {e}")
            raise InternalErrorException

    async def delete_membership(
        self, uow: UnitOfWork, membership_id: UUID, current_user_id: UUID
    ) -> None:
        try:
            memberships, _ = await uow.membership.read(
                field="id", value=membership_id, offset=0, limit=1
            )

            if not memberships:
                raise MembershipNotFound

            membership = memberships[0]

            await check_owner_permission(current_user_id, uow, membership.company_id)

            await uow.membership.delete_by("id", membership_id)
            await uow.session.flush()

        except (NotOwnerOfCompany, MembershipNotFound):
            raise
        except Exception as e:
            logger.exception(f"Error while deleting membership: {e}")
            raise InternalErrorException
