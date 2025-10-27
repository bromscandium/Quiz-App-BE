import pytest
from uuid import uuid4

from app.exceptions.base import InternalErrorException
from app.services.company import CompanyService
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.exceptions.company import CompanyNotFound
from app.exceptions.user import UnauthorizedUserAction
from tests.fixtures import test_user

company_service = CompanyService()


@pytest.mark.asyncio
class TestCompanyService:
    async def test_create_company_success(self, uow, test_user):
        data = CompanyCreate(
            name="Acme Corp", description="A test company", visibility=True
        )
        company = await company_service.create_company(uow, test_user.id, data)

        assert company.id is not None
        assert company.name == data.name
        assert company.description == data.description
        assert company.owner.id == test_user.id
        assert company.visibility is True
        assert company.created_at is not None
        assert company.updated_at is not None

    async def test_get_company_by_id_success(self, uow, test_user):
        data = CompanyCreate(
            name="Beta LLC", description="Another company", visibility=False
        )
        created = await company_service.create_company(uow, test_user.id, data)
        fetched = await company_service.read_company_by_id(uow, created.id)

        assert fetched.id == created.id
        assert fetched.name == created.name
        assert fetched.description == created.description
        assert fetched.owner.id == test_user.id

    async def test_get_company_by_id_not_found(self, uow):
        company = await company_service.read_company_by_id(uow, uuid4())
        assert company is None

    async def test_read_all_companies(self, uow, test_user):
        company1 = await company_service.create_company(
            uow,
            test_user.id,
            CompanyCreate(name="Company One", description="Desc 1", visibility=True),
        )
        company2 = await company_service.create_company(
            uow,
            test_user.id,
            CompanyCreate(name="Company Two", description="Desc 2", visibility=False),
        )

        result = await company_service.read_all_companies(uow, offset=0, limit=10)
        assert result.total >= 2
        names = [c.name for c in result.companies]
        assert company1.name in names
        assert company2.name in names

    async def test_read_all_companies_pagination(self, uow, test_user):
        await company_service.create_company(
            uow,
            test_user.id,
            CompanyCreate(name="Company One", description="Desc 1", visibility=True),
        )
        await company_service.create_company(
            uow,
            test_user.id,
            CompanyCreate(name="Company Two", description="Desc 2", visibility=False),
        )

        page1 = await company_service.read_all_companies(uow, offset=0, limit=1)
        page2 = await company_service.read_all_companies(uow, offset=1, limit=1)

        assert len(page1.companies) == 1
        assert len(page2.companies) == 1
        assert page1.companies[0].id != page2.companies[0].id

    async def test_update_company_success(self, uow, test_user):
        company = await company_service.create_company(
            uow,
            test_user.id,
            CompanyCreate(name="Original", description="Orig Desc", visibility=True),
        )

        update_data = CompanyUpdate(
            name="Updated", description="Updated Desc", visibility=False
        )
        updated = await company_service.update_company(
            uow, company.id, update_data, test_user.id
        )

        assert updated.id == company.id
        assert updated.name == "Updated"
        assert updated.description == "Updated Desc"
        assert updated.visibility is False

    async def test_update_company_partial(self, uow, test_user):
        company = await company_service.create_company(
            uow,
            test_user.id,
            CompanyCreate(name="Original", description="Orig Desc", visibility=True),
        )

        update_data = CompanyUpdate(name="Updated Only Name")
        updated = await company_service.update_company(
            uow, company.id, update_data, test_user.id
        )

        assert updated.name == "Updated Only Name"
        assert updated.description == "Orig Desc"
        assert updated.visibility is True

    async def test_update_company_unauthorized(self, uow, test_user):
        company = await company_service.create_company(
            uow,
            test_user.id,
            CompanyCreate(name="Original", description="Orig Desc", visibility=True),
        )

        other_user_id = uuid4()
        update_data = CompanyUpdate(name="Hacked")

        with pytest.raises(InternalErrorException):
            await company_service.update_company(
                uow, company.id, update_data, other_user_id
            )

    async def test_update_company_not_found(self, uow, test_user):
        update_data = CompanyUpdate(name="Updated")

        with pytest.raises(CompanyNotFound):
            await company_service.update_company(
                uow, uuid4(), update_data, test_user.id
            )

    async def test_delete_company_success(self, uow, test_user):
        company = await company_service.create_company(
            uow,
            test_user.id,
            CompanyCreate(
                name="ToDelete", description="Will be deleted", visibility=True
            ),
        )

        await company_service.delete_company(uow, company.id, test_user.id)
        deleted = await company_service.read_company_by_id(uow, company.id)
        assert deleted is None

    async def test_delete_company_unauthorized(self, uow, test_user):
        company = await company_service.create_company(
            uow,
            test_user.id,
            CompanyCreate(
                name="ToDelete", description="Will be deleted", visibility=True
            ),
        )

        other_user_id = uuid4()
        with pytest.raises(InternalErrorException):
            await company_service.delete_company(uow, company.id, other_user_id)

    async def test_delete_company_not_found(self, uow, test_user):
        with pytest.raises(CompanyNotFound):
            await company_service.delete_company(uow, uuid4(), test_user.id)
