from uuid import UUID

from app.enums.roles import Roles
from app.enums.statuses import Statuses
from app.exceptions.base import InternalErrorException
from app.exceptions.company_actions import (
    NotProvidedInfoForInvitation,
    NotFoundActionType,
    PrivateCompany,
    NotAllowedChangeCompanyAction,
    CompanyActionNotFound,
)
from app.exceptions.user import UnauthorizedUserAction
from app.permissions.company import check_company_visibility
from app.schemas.company_actions import (
    CompanyActionSchema,
    CompanyActionUpdate,
    CompanyActionCreate,
    CompanyActionsList,
)
from app.schemas.membership import MembershipCreate
from app.services.membership import MembershipService
from app.unit_of_work.uow import UnitOfWork
from app.enums.action_types import ActionTypes
from app.permissions.membership import check_owner_permission
from app.utils.logger import logger


class CompanyActionsService:
    def __init__(self):
        self.membership_service = MembershipService()

    async def _get_company_action_by_id(self, uow: UnitOfWork, action_id: UUID):
        items, _ = await uow.company_actions.read(
            field="id",
            value=action_id,
            offset=0,
            limit=1,
            load_relationships=["user", "company", "company.owner"],
            use_joined_load=False,
        )

        if not items:
            raise CompanyActionNotFound

        return items[0]

    async def create_company_action(
        self, uow: UnitOfWork, current_user_id: UUID, data: CompanyActionCreate
    ) -> CompanyActionSchema:
        try:
            if data.action_type == ActionTypes.INVITATION:
                await check_owner_permission(
                    current_user_id, uow, company_id=data.company_id
                )
                if data.user_id is None and data.invited_email is None:
                    raise NotProvidedInfoForInvitation

            elif data.action_type == ActionTypes.REQUEST:
                is_public = await check_company_visibility(
                    company_id=data.company_id, uow=uow
                )
                if not is_public:
                    raise PrivateCompany
                if current_user_id != data.user_id:
                    raise UnauthorizedUserAction
            else:
                raise NotFoundActionType

            company_action = await uow.company_actions.create(**data.model_dump())
            await uow.session.flush()

            company_action = await self._get_company_action_by_id(
                uow, company_action.id
            )

            return CompanyActionSchema.model_validate(company_action)
        except (
            NotFoundActionType,
            NotProvidedInfoForInvitation,
            UnauthorizedUserAction,
            PrivateCompany,
        ):
            raise
        except Exception as e:
            logger.exception(f"Error while creating company action: {e}")
            raise InternalErrorException

    async def read_company_action_by_id(
        self, uow: UnitOfWork, current_user_id: UUID, company_action_id: UUID
    ) -> CompanyActionSchema:
        try:
            company_action = await self._get_company_action_by_id(
                uow, company_action_id
            )

            if company_action.action_type == ActionTypes.INVITATION:
                is_owner = await check_owner_permission(
                    current_user_id, uow, company_action.company_id
                )
                is_invited_user = current_user_id == company_action.user_id

                if not is_owner and not is_invited_user:
                    raise UnauthorizedUserAction

            elif company_action.action_type == ActionTypes.REQUEST:
                is_owner = await check_owner_permission(
                    current_user_id, uow, company_action.company_id
                )
                is_requesting_user = current_user_id == company_action.user_id

                if not is_owner and not is_requesting_user:
                    raise UnauthorizedUserAction
            else:
                raise NotFoundActionType

            return CompanyActionSchema.model_validate(company_action)

        except (NotFoundActionType, UnauthorizedUserAction, CompanyActionNotFound):
            raise
        except Exception as e:
            logger.exception(f"Error while reading company action by id: {e}")
            raise InternalErrorException

    async def read_company_actions(
        self,
        uow: UnitOfWork,
        current_user_id: UUID,
        action_type: ActionTypes | None = None,
        company_id: UUID | None = None,
        status: Statuses | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> CompanyActionsList:
        try:
            if company_id:
                await check_owner_permission(current_user_id, uow, company_id)
                items, total = await uow.company_actions.read(
                    field="company_id",
                    value=company_id,
                    offset=offset,
                    limit=limit,
                    load_relationships=["user", "company", "company.owner"],
                )

                if action_type == ActionTypes.INVITATION:
                    filtered_items = [
                        c for c in items if c.action_type == ActionTypes.INVITATION
                    ]
                elif action_type == ActionTypes.REQUEST:
                    filtered_items = [
                        c for c in items if c.action_type == ActionTypes.REQUEST
                    ]
                else:
                    filtered_items = items
            else:
                items, total = await uow.company_actions.read(
                    field="user_id",
                    value=current_user_id,
                    offset=offset,
                    limit=limit,
                    load_relationships=["user", "company", "company.owner"],
                )

                if action_type == ActionTypes.INVITATION:
                    filtered_items = [
                        c for c in items if c.action_type == ActionTypes.INVITATION
                    ]
                elif action_type == ActionTypes.REQUEST:
                    filtered_items = [
                        c for c in items if c.action_type == ActionTypes.REQUEST
                    ]
                else:
                    filtered_items = items

            if status is not None:
                filtered_items = [c for c in filtered_items if c.status == status]

            validated_items = [
                CompanyActionSchema.model_validate(c) for c in filtered_items
            ]

            return CompanyActionsList(
                actions=validated_items,
                total=len(filtered_items),
                pending_total=sum(
                    1 for c in filtered_items if c.status == Statuses.PENDING
                ),
                accepted_total=sum(
                    1 for c in filtered_items if c.status == Statuses.ACCEPTED
                ),
                cancelled_total=sum(
                    1 for c in filtered_items if c.status == Statuses.CANCELLED
                ),
            )
        except UnauthorizedUserAction:
            raise
        except Exception as e:
            logger.exception(f"Error while reading company actions: {e}")
            raise InternalErrorException

    async def update_company_action(
        self,
        uow: UnitOfWork,
        current_user_id: UUID,
        company_action_id: UUID,
        data: CompanyActionUpdate,
    ) -> CompanyActionSchema:
        try:
            company_action = await self._get_company_action_by_id(
                uow, company_action_id
            )

            if company_action.status != Statuses.PENDING:
                raise NotAllowedChangeCompanyAction

            if company_action.action_type == ActionTypes.INVITATION:
                if current_user_id != company_action.user_id:
                    raise UnauthorizedUserAction

            elif company_action.action_type == ActionTypes.REQUEST:
                await check_owner_permission(
                    current_user_id, uow, company_action.company_id
                )
            else:
                raise NotFoundActionType

            if data.status == Statuses.ACCEPTED:
                membership_data = MembershipCreate(
                    user_id=company_action.user_id,
                    company_id=company_action.company_id,
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

        except (
            NotFoundActionType,
            NotAllowedChangeCompanyAction,
            UnauthorizedUserAction,
            CompanyActionNotFound,
        ):
            raise
        except Exception as e:
            logger.exception(f"Error while updating company action: {e}")
            raise InternalErrorException

    async def delete_company_action(
        self, uow: UnitOfWork, current_user_id: UUID, company_action_id: UUID
    ) -> None:
        try:
            company_action = await self._get_company_action_by_id(
                uow, company_action_id
            )

            if company_action.action_type == ActionTypes.INVITATION:
                await check_owner_permission(
                    current_user_id, uow, company_action.company_id
                )

            elif company_action.action_type == ActionTypes.REQUEST:
                if current_user_id != company_action.user_id:
                    raise UnauthorizedUserAction
            else:
                raise NotFoundActionType

            await uow.company_actions.delete_by("id", company_action_id)
            await uow.session.flush()

        except (UnauthorizedUserAction, NotFoundActionType, CompanyActionNotFound):
            raise
        except Exception as e:
            logger.exception(f"Error while deleting company action: {e}")
            raise InternalErrorException
