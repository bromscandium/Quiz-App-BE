from uuid import UUID

from app.enums import *
from app.exceptions import (
    CompanyActionNotFound,
    NotAllowedChangeCompanyAction,
    NotFoundActionType,
    PrivateCompany,
    UnauthorizedUserAction,
    UnauthorizedCompanyOwner,
    NotProvidedInfoForCompanyAction,
)

from app.permissions import *
from app.schemas.company_actions import (
    CompanyActionCreate,
    CompanyActionSchema,
    CompanyActionsList,
    CompanyActionUpdate,
)
from app.schemas.membership import MembershipCreate
from app.services.membership import MembershipService
from app.unit_of_work import UnitOfWork
from app.utils import LoggerUtil


class CompanyActionsService:
    def __init__(self):
        self.membership_service = MembershipService()
        self.logger_util = LoggerUtil()

    async def _get_company_action_by_id(
            self, uow: UnitOfWork, action_id: UUID
    ) -> CompanyActionSchema | None:
        company_action, _ = await uow.company_actions.read(
            field="id",
            value=action_id,
            offset=0,
            limit=20,
            load_relationships=["user", "company", "company.owner"],
            use_joined_load=False,
        )

        if not company_action:
            return None

        return company_action[0]

    async def _validate_user_permission(
            self, uow: UnitOfWork, company_action: CompanyActionSchema, user_id: UUID
    ):
        is_owner = await check_owner_permission(user_id, uow, company_action.company.id)
        is_current_user = user_id == company_action.user.id

        if not is_owner and not is_current_user:
            self.logger_util.info("Cannot validate user permission")
            raise UnauthorizedUserAction

    async def create_company_action(
            self, uow: UnitOfWork, current_user_id: UUID, data: CompanyActionCreate
    ) -> CompanyActionSchema:
        if data.action_type == ActionTypes.INVITATION:
            if not await check_owner_permission(
                    current_user_id, uow, company_id=data.company_id
            ):
                self.logger_util.info("Cannot create invitation action")
                raise UnauthorizedCompanyOwner
            if data.user_id is None and data.invited_email is None:
                self.logger_util.info(
                    "Cannot create invitation action without user or invited email"
                )
                raise NotProvidedInfoForCompanyAction

        elif data.action_type == ActionTypes.REQUEST:
            is_public = await check_company_visibility(
                company_id=data.company_id, uow=uow
            )
            if not is_public:
                self.logger_util.info("Cannot create request action")
                raise PrivateCompany
            if current_user_id != data.user_id:
                self.logger_util.info(
                    "Cannot create request action without current user"
                )
                raise NotProvidedInfoForCompanyAction
        else:
            self.logger_util.info("Cannot create company action")
            raise NotFoundActionType

        company_action = await uow.company_actions.create(**data.model_dump())
        await uow.session.flush()

        company_action = await self._get_company_action_by_id(uow, company_action.id)

        return CompanyActionSchema.model_validate(company_action)

    async def read_company_action_by_id(
            self, uow: UnitOfWork, current_user_id: UUID, company_action_id: UUID
    ) -> CompanyActionSchema:
        company_action = await self._get_company_action_by_id(uow, company_action_id)

        await self._validate_user_permission(uow, company_action, current_user_id)

        return CompanyActionSchema.model_validate(company_action)

    async def read_company_actions(
            self,
            uow: UnitOfWork,
            current_user_id: UUID,
            action_type: ActionTypes | None = None,
            company_id: UUID | None = None,
            status: ActionStatuses | None = None,
            offset: int = 0,
            limit: int = 20,
    ) -> CompanyActionsList:
        if company_id:
            if not await check_owner_permission(current_user_id, uow, company_id):
                self.logger_util.info("User is not owner")
                raise UnauthorizedCompanyOwner
            company_actions, total = await uow.company_actions.read(
                field="company_id",
                value=company_id,
                offset=offset,
                limit=limit,
                load_relationships=["user", "company", "company.owner"],
            )

        else:
            company_actions, total = await uow.company_actions.read(
                field="user_id",
                value=current_user_id,
                offset=offset,
                limit=limit,
                load_relationships=["user", "company", "company.owner"],
            )

        if action_type == ActionTypes.INVITATION:
            filtered_items = [
                c_a
                for c_a in company_actions
                if c_a.action_type == ActionTypes.INVITATION
            ]
        elif action_type == ActionTypes.REQUEST:
            filtered_items = [
                c_a for c_a in company_actions if c_a.action_type == ActionTypes.REQUEST
            ]
        else:
            filtered_items = company_actions

        if status is not None:
            filtered_items = [c_a for c_a in filtered_items if c_a.status == status]

        validated_items = [
            CompanyActionSchema.model_validate(c_a) for c_a in filtered_items
        ]

        return CompanyActionsList(
            actions=validated_items,
            total=len(filtered_items),
            pending_total=sum(
                1 for c_a in filtered_items if c_a.status == ActionStatuses.PENDING
            ),
            accepted_total=sum(
                1 for c_a in filtered_items if c_a.status == ActionStatuses.ACCEPTED
            ),
            cancelled_total=sum(
                1 for c_a in filtered_items if c_a.status == ActionStatuses.CANCELLED
            ),
        )

    async def update_company_action(
            self,
            uow: UnitOfWork,
            current_user_id: UUID,
            company_action_id: UUID,
            data: CompanyActionUpdate,
    ) -> CompanyActionSchema:
        company_action = await self._get_company_action_by_id(uow, company_action_id)
        if company_action is None:
            self.logger_util.info("Company action not found")
            raise CompanyActionNotFound

        if company_action.status == ActionStatuses.PENDING:
            await self._validate_user_permission(uow, company_action, current_user_id)

            if data.status == ActionStatuses.ACCEPTED:
                membership_data = MembershipCreate(
                    user_id=company_action.user.id,
                    company_id=company_action.company.id,
                    role=Roles.MEMBER,
                    is_active=True,
                )

                await self.membership_service.create_membership(
                    uow=uow, data=membership_data
                )

            company_action.status = data.status
            await uow.session.flush()
            await uow.session.refresh(
                company_action, attribute_names=["user", "company"]
            )

            return CompanyActionSchema.model_validate(company_action)
        else:
            self.logger_util.info("Cannot update company action")
            raise NotAllowedChangeCompanyAction

    async def delete_company_action(
            self, uow: UnitOfWork, current_user_id: UUID, company_action_id: UUID
    ) -> None:
        company_action = await self._get_company_action_by_id(uow, company_action_id)
        if company_action is None:
            self.logger_util.info("Company action not found")
            raise CompanyActionNotFound

        await self._validate_user_permission(uow, company_action, current_user_id)

        await uow.company_actions.delete_by("id", company_action_id)
