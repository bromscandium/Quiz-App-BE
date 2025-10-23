from datetime import datetime

import pytest

from app.exceptions.invitation import NotProvidedInfoForInvitation
from app.models.enums import Statuses
from app.schemas.invitation import InvitationSchema, InvitationUpdateRequest
from app.services.invitation import InvitationService
from tests.fixtures import test_user, test_second_user, test_company

service = InvitationService()


@pytest.mark.asyncio
class TestInvitationService:
    async def test_send_invitation(
        self, uow, test_user, test_second_user, test_company
    ):
        data = InvitationSchema(
            company_id=test_company.id, user_id=test_second_user.id, invited_email=None
        )
        invitation = await service.send_invitation(
            uow=uow, current_user_id=test_user.id, data=data
        )

        assert invitation.company_id == test_company.id
        assert invitation.user_id == test_second_user.id
        assert invitation.status == Statuses.PENDING

    async def test_send_email_invitation(
        self, uow, test_user, test_second_user, test_company
    ):
        data = InvitationSchema(
            company_id=test_company.id, user_id=None, invited_email="testtest@test.com"
        )
        invitation = await service.send_invitation(
            uow=uow, current_user_id=test_user.id, data=data
        )

        assert invitation.company_id == test_company.id
        assert invitation.invited_email == "testtest@test.com"
        assert invitation.status == Statuses.PENDING

    async def test_send_invitation_error(self, uow, test_user, test_company):
        data = InvitationSchema(
            company_id=test_company.id, user_id=None, invited_email=None
        )
        with pytest.raises(NotProvidedInfoForInvitation):
            await service.send_invitation(
                uow=uow, current_user_id=test_user.id, data=data
            )

    async def test_invitation_update(
        self, uow, test_user, test_second_user, test_company
    ):
        data = InvitationSchema(
            company_id=test_company.id, user_id=test_second_user.id, invited_email=None
        )
        invitation = await service.send_invitation(
            uow=uow, current_user_id=test_user.id, data=data
        )
        update_data = InvitationUpdateRequest(
            status=Statuses.ACCEPTED,
            decision_time=datetime.now(),
            company_id=test_company.id,
            user_id=test_second_user.id,
        )
        updated_req = await service.update_invitation(
            uow, test_user.id, invitation.id, update_data
        )

        assert updated_req.status == Statuses.ACCEPTED

    async def test_get_user_requests(
        self, uow, test_user, test_second_user, test_company
    ):
        data = InvitationSchema(
            company_id=test_company.id, user_id=test_second_user.id, invited_email=None
        )
        await service.send_invitation(uow=uow, current_user_id=test_user.id, data=data)

        response = await service.get_user_invitations(uow, test_second_user.id)
        assert len(response.invitations) >= 1
        for r in response.invitations:
            assert r.user_id == test_second_user.id

    async def test_get_company_requests(
        self, uow, test_user, test_second_user, test_company
    ):
        data = InvitationSchema(
            company_id=test_company.id, user_id=test_second_user.id, invited_email=None
        )
        await service.send_invitation(uow=uow, current_user_id=test_user.id, data=data)

        response = await service.get_company_invitations(
            uow, test_user.id, test_company.id
        )
        assert len(response.invitations) >= 1
        for r in response.invitations:
            assert r.company_id == test_company.id
