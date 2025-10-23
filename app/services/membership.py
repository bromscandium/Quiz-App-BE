from uuid import UUID

from sqlalchemy import func

from app.exceptions.membership import (
    NoMembershipFoundException,
    MembershipInternalErrorException,
)
from app.permissions.membership import check_owner_permission
from app.schemas.membership import (
    MembershipDetailResponse,
    MembershipCreateRequest,
    MembershipUpdateRequest,
    MembershipListResponse,
)

from app.unit_of_work.uow import UnitOfWork
from app.utils.logger import logger


class MembershipService:
    async def create_membership(
        self, uow: UnitOfWork, data: MembershipCreateRequest, current_user_id: UUID
    ) -> MembershipDetailResponse:
        try:
            await check_owner_permission(current_user_id, uow)

            membership = await uow.membership.create(**data.model_dump())
            await uow.session.flush()
            return MembershipDetailResponse.model_validate(membership)

        except Exception as e:
            logger.exception(f"Error while creating membership: {e}")
            raise MembershipInternalErrorException

    async def get_membership_by_id(
        self, uow: UnitOfWork, membership_id: UUID
    ) -> MembershipDetailResponse | None:
        try:
            items, _ = await uow.users.read(
                field="id", value=membership_id, offset=0, limit=1
            )
            membership = items[0] if items else None
            if not membership:
                return None
            return MembershipDetailResponse.model_validate(membership)
        except Exception as e:
            logger.exception(f"Error while fetching membership by id: {e}")
            raise MembershipInternalErrorException

    async def get_user_memberships(
        self, uow: UnitOfWork, user_id: UUID, offset: int = 0, limit: int = 20
    ) -> MembershipListResponse:
        items, total = await uow.membership.read(
            field="user_id", value=user_id, offset=offset, limit=limit
        )
        memberships = [MembershipDetailResponse.model_validate(m) for m in items]
        return MembershipListResponse(memberships=memberships, total=total)

    async def get_company_members(
        self, uow: UnitOfWork, company_id: UUID, offset: int = 0, limit: int = 20
    ) -> MembershipListResponse:
        items, total = await uow.membership.read(
            field="company_id", value=company_id, offset=offset, limit=limit
        )
        memberships = [MembershipDetailResponse.model_validate(m) for m in items]
        return MembershipListResponse(memberships=memberships, total=total)

    async def update_membership(
        self,
        uow: UnitOfWork,
        membership_id: UUID,
        current_user_id: UUID,
        data: MembershipUpdateRequest,
    ) -> MembershipDetailResponse:
        try:
            await check_owner_permission(current_user_id, uow)
            update_data = data.model_dump(exclude_unset=True)
            membership = await uow.membership.update_by(
                "id", membership_id, **update_data
            )
            return MembershipDetailResponse.model_validate(membership)
        except Exception as e:
            logger.exception(f"Error while updating membership: {e}")
            raise MembershipInternalErrorException

    async def delete_membership(
        self,
        uow: UnitOfWork,
        membership_id: UUID,
        current_user_id: UUID,
    ) -> MembershipDetailResponse:
        try:
            await check_owner_permission(current_user_id, uow)
            membership = await uow.membership.update_by(
                "id", membership_id, is_active=False, left_at=func.now()
            )
            if not membership:
                raise NoMembershipFoundException
            return MembershipDetailResponse.model_validate(membership)
        except NoMembershipFoundException:
            raise NoMembershipFoundException
        except Exception as e:
            logger.exception(f"Error while deleting membership: {e}")
            raise MembershipInternalErrorException

    async def cancel_membership(
        self,
        uow: UnitOfWork,
        membership_id: UUID,
        current_user_id: UUID,
    ) -> MembershipDetailResponse:
        try:
            membership, _ = await uow.membership.read(
                field="id", value=membership_id, offset=0, limit=1
            )
            if not membership:
                raise NoMembershipFoundException

            if membership[0].user_id != current_user_id:
                raise MembershipInternalErrorException(
                    "User cannot cancel others' memberships"
                )

            membership[0] = await uow.membership.update_by(
                "id", membership_id, is_active=False, left_at=func.now()
            )

            return MembershipDetailResponse.model_validate(membership[0])
        except NoMembershipFoundException:
            raise NoMembershipFoundException
        except Exception as e:
            logger.exception(f"Error while canceling membership: {e}")
            raise MembershipInternalErrorException
