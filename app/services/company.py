from uuid import UUID

from app.models.enums import Roles
from app.schemas.membership import MembershipCreateRequest
from app.exceptions.user import UnauthorizedUserActionException
from app.services.membership import MembershipService
from app.unit_of_work.uow import UnitOfWork
from app.schemas.company import (
    CompanyCreateRequest,
    CompanyUpdateRequest,
    CompanyDetailResponse,
    CompaniesListResponse,
)
from app.exceptions.company import (
    CompanyNotFoundException,
    CompanyInternalErrorException,
)
from app.utils.logger import logger


class CompanyService:
    def __init__(self):
        self.membership_service = MembershipService()

    async def create_company(
        self, uow: UnitOfWork, current_user_id: UUID, data: CompanyCreateRequest
    ) -> CompanyDetailResponse:
        try:
            company = await uow.company.create(
                owner_id=current_user_id,
                name=data.name,
                description=data.description,
                visibility=data.visibility,
            )
            await uow.session.flush()

            membership_data = MembershipCreateRequest(
                company_id=company.id,
                user_id=current_user_id,
                role=Roles.OWNER,
                is_active=True,
            )

            await self.membership_service.create_membership(
                uow=uow, current_user_id=current_user_id, data=membership_data
            )

            return CompanyDetailResponse.model_validate(company)
        except Exception as e:
            logger.exception(f"Error creating company: {e}")
            raise CompanyInternalErrorException

    async def get_company_by_id(
        self, uow: UnitOfWork, company_id: UUID
    ) -> CompanyDetailResponse:
        try:
            company, _ = await uow.company.read(
                field="id", value=company_id, offset=0, limit=1
            )
            if not company:
                raise CompanyNotFoundException
            return CompanyDetailResponse.model_validate(company[0])
        except CompanyNotFoundException:
            raise CompanyNotFoundException
        except Exception as e:
            logger.exception(f"Error fetching company: {e}")
            raise CompanyInternalErrorException

    async def read_all_companies(
        self, uow: UnitOfWork, offset: int = 0, limit: int = 20
    ) -> CompaniesListResponse:
        items, total = await uow.company.read(offset=offset, limit=limit)
        company_schemas = [
            CompanyDetailResponse.model_validate(company) for company in items
        ]
        return CompaniesListResponse(companies=company_schemas, total=total)

    async def update_company(
        self,
        uow: UnitOfWork,
        company_id: UUID,
        current_user_id: UUID,
        data: CompanyUpdateRequest,
    ) -> CompanyDetailResponse:
        try:
            company = await self.get_company_by_id(uow, company_id)
            if not company:
                raise CompanyNotFoundException

            if company.owner_id != current_user_id:
                raise UnauthorizedUserActionException

            update_data = data.model_dump(exclude_unset=True)
            company = await uow.company.update_by("id", company_id, **update_data)
            return CompanyDetailResponse.model_validate(company)
        except (UnauthorizedUserActionException, CompanyNotFoundException):
            raise
        except Exception as e:
            logger.exception(f"Error updating company: {e}")
            raise CompanyInternalErrorException

    async def delete_company(
        self, uow: UnitOfWork, company_id: UUID, current_user_id: UUID
    ) -> CompanyDetailResponse:
        try:
            company = await self.get_company_by_id(uow, company_id)
            if not company:
                raise CompanyNotFoundException

            if company.owner_id != current_user_id:
                raise UnauthorizedUserActionException

            await uow.company.delete_by("id", company_id)
            logger.info("Company deleted")

            return company
        except (CompanyNotFoundException, UnauthorizedUserActionException):
            raise
        except Exception as e:
            logger.exception(f"Error deleting company: {e}")
            raise CompanyInternalErrorException
