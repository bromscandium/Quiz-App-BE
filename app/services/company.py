from uuid import UUID

from app.enums.roles import Roles
from app.exceptions import CompanyNotFound, UnauthorizedCompanyOwner
from app.permissions import check_owner_permission
from app.schemas.company import (
    CompaniesList,
    CompanyCreate,
    CompanySchema,
    CompanyUpdate,
)
from app.schemas.membership import MembershipCreate
from app.services.membership import MembershipService
from app.unit_of_work import UnitOfWork
from app.utils import LoggerUtil


class CompanyService:
    def __init__(self):
        self.membership_service = MembershipService()
        self.logger_util = LoggerUtil()

    async def create_company(
        self, uow: UnitOfWork, current_user_id: UUID, data: CompanyCreate
    ) -> CompanySchema:
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

        await self.membership_service.create_membership(uow=uow, data=membership_data)

        return CompanySchema.model_validate(company)

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
        companies, total = await uow.company.read(
            offset=offset, limit=limit, load_relationships=["owner"]
        )
        company_schemas = [CompanySchema.model_validate(c) for c in companies]
        return CompaniesList(companies=company_schemas, total=total)

    async def update_company(
        self,
        uow: UnitOfWork,
        company_id: UUID,
        data: CompanyUpdate,
        current_user_id: UUID,
    ) -> CompanySchema:
        if not await check_owner_permission(current_user_id, uow, company_id):
            self.logger_util.info("User is not authorized owner")
            raise UnauthorizedCompanyOwner

        if await self.read_company_by_id(uow, company_id) is None:
            self.logger_util.info("Company not found")
            raise CompanyNotFound

        update_data = data.model_dump(exclude_unset=True)
        company = await uow.company.update_by("id", company_id, **update_data)
        return CompanySchema.model_validate(company)

    async def delete_company(
        self, uow: UnitOfWork, company_id: UUID, current_user_id: UUID
    ) -> None:
        if not await check_owner_permission(current_user_id, uow, company_id):
            self.logger_util.info("User is not authorized owner")
            raise UnauthorizedCompanyOwner

        if await self.read_company_by_id(uow, company_id) is None:
            self.logger_util.info("Company not found")
            raise CompanyNotFound

        await uow.company.delete_by("id", company_id)
