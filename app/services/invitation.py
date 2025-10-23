from uuid import UUID

from app.exceptions.invitation import (
    InvitationInternalErrorException,
    NotProvidedInfoForInvitation,
    InvitationNotFound,
)
from app.models.enums import Statuses
from app.permissions.membership import check_owner_permission
from app.schemas.invitation import (
    InvitationDetailResponse,
    InvitationListResponse,
    InvitationSchema,
    InvitationUpdateRequest,
)
from app.schemas.membership import MembershipCreateRequest

from app.services.user import UserService
from app.unit_of_work.uow import UnitOfWork
from app.utils.logger import logger


class InvitationService:
    def __init__(self):
        self.user_service = UserService()

    async def send_invitation(
        self, uow: UnitOfWork, current_user_id: UUID, data: InvitationSchema
    ) -> InvitationDetailResponse:
        try:
            await check_owner_permission(current_user_id, uow)

            if data.user_id is None and data.invited_email is None:
                raise NotProvidedInfoForInvitation

            invitation = await uow.invitation.create(**data.model_dump())
            await uow.session.flush()

            return InvitationDetailResponse.model_validate(invitation)
        except NotProvidedInfoForInvitation:
            raise NotProvidedInfoForInvitation
        except Exception as e:
            logger.exception(f"Error while sending invitation: {e}")
            raise InvitationInternalErrorException

    async def update_invitation(
        self,
        uow: UnitOfWork,
        current_user_id: UUID,
        invitation_id: UUID,
        data: InvitationUpdateRequest,
    ) -> InvitationDetailResponse:
        try:
            if data.status == Statuses.CANCELLED:
                await check_owner_permission(current_user_id, uow)

            invitation = await uow.invitation.update_by(
                "id",
                invitation_id,
                status=data.status,
                decision_time=data.decision_time,
            )
            if not invitation:
                raise InvitationNotFound
            await uow.session.flush()

            if data.status == Statuses.ACCEPTED:
                new_member_data = MembershipCreateRequest(
                    company_id=data.company_id,
                    user_id=data.user_id,
                )

                await uow.membership.create(**new_member_data.model_dump())

            return InvitationDetailResponse.model_validate(invitation)
        except InvitationNotFound:
            raise InvitationNotFound
        except Exception as e:
            logger.exception(f"Error while cancelling invitation: {e}")
            raise InvitationInternalErrorException

    async def get_company_invitations(
        self,
        uow: UnitOfWork,
        current_user_id: UUID,
        company_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> InvitationListResponse:
        await check_owner_permission(current_user_id, uow)
        invitations, total = await uow.invitation.read(
            "company_id", company_id, offset, limit
        )
        invitations_details = [
            InvitationDetailResponse.model_validate(invitation)
            for invitation in invitations
        ]
        return InvitationListResponse(invitations=invitations_details, total=total)

    async def get_user_invitations(
        self, uow: UnitOfWork, current_user_id: UUID, offset: int = 0, limit: int = 20
    ) -> InvitationListResponse:
        invitations, total = await uow.invitation.read(
            "user_id", current_user_id, offset, limit
        )
        invitations_details = [
            InvitationDetailResponse.model_validate(invitation)
            for invitation in invitations
        ]
        return InvitationListResponse(invitations=invitations_details, total=total)
