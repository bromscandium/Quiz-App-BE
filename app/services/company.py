from uuid import UUID

from app.enums.roles import Roles
from app.exceptions.base import InternalErrorException
from app.permissions.ownership import check_owner_permission
from app.schemas.membership import MembershipCreate
from app.exceptions.user import UnauthorizedUserAction
from app.services.membership import MembershipService
from app.unit_of_work.uow import UnitOfWork
from app.schemas.company import (
    CompanySchema,
    CompanyCreate,
    CompanyUpdate,
    CompaniesList,
)
from app.exceptions.company import (
    CompanyNotFound,
)
from app.utils.logger import logger


class CompanyService:
    def __init__(self):
        self.membership_service = MembershipService()

    async def create_company(
        self, uow: UnitOfWork, current_user_id: UUID, data: CompanyCreate
    ) -> CompanySchema:
        try:
            company = await uow.company.create(
                owner_id=current_user_id, **data.model_dump()
            )
            await uow.session.flush()
            await uow.session.refresh(company, ["owner"])

            membership_data = MembershipCreate(
                user_id=current_user_id,
                company_id=company.id,
                role=Roles.OWNER,
                is_active=True,
            )

            await self.membership_service.create_membership(
                uow=uow, data=membership_data
            )

            return CompanySchema.model_validate(company)

        except Exception as e:
            logger.exception(f"Error creating company: {e}")
            raise InternalErrorException

    async def read_company_by_id(
        self, uow: UnitOfWork, value: UUID
    ) -> CompanySchema | None:
        company, _ = await uow.company.read(
            field="id", value=value, offset=0, limit=1, load_relationships=["owner"]
        )
        if not company:
            return None
        return CompanySchema.model_validate(company[0])

    async def read_all_companies(
        self, uow: UnitOfWork, offset: int = 0, limit: int = 20
    ) -> CompaniesList:
        items, total = await uow.company.read(
            offset=offset, limit=limit, load_relationships=["owner"]
        )
        company_schemas = [CompanySchema.model_validate(c) for c in items]
        return CompaniesList(companies=company_schemas, total=total)

    async def update_company(
        self,
        uow: UnitOfWork,
        company_id: UUID,
        data: CompanyUpdate,
        current_user_id: UUID,
    ) -> CompanySchema:
        try:
            company = await self.read_company_by_id(uow, company_id)
            if not company:
                raise CompanyNotFound

            await check_owner_permission(current_user_id, uow, company_id)

            update_data = data.model_dump(exclude_unset=True)
            company = await uow.company.update_by("id", company_id, **update_data)
            return CompanySchema.model_validate(company)
        except (UnauthorizedUserAction, CompanyNotFound):
            raise
        except Exception as e:
            logger.exception(f"Error updating company: {e}")
            raise InternalErrorException

    async def delete_company(
        self, uow: UnitOfWork, company_id: UUID, current_user_id: UUID
    ) -> None:
        try:
            company = await self.read_company_by_id(uow, company_id)
            if not company:
                raise CompanyNotFound

            await check_owner_permission(current_user_id, uow, company_id)

            await uow.company.delete_by("id", company_id)

        except (CompanyNotFound, UnauthorizedUserAction):
            raise
        except Exception as e:
            logger.exception(f"Error deleting company: {e}")
            raise InternalErrorException
