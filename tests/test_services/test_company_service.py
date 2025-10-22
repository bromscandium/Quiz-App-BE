import pytest
from uuid import uuid4
from app.services.company_service import CompanyService
from app.schemas.company_schema import CompanyCreate, CompanyUpdateRequest
from app.exceptions.company_exceptions import CompanyNotFoundException
from app.exceptions.user_exceptions import UnauthorizedUserActionException

company_service = CompanyService()


@pytest.mark.asyncio
class TestCompanyService:
    async def test_create_company_success(self, uow, test_user):
        company_data = CompanyCreate(
            name="Acme Corp", description="A test company", visibility=True
        )
        company = await company_service.create_company(uow, test_user.id, company_data)

        assert company.id is not None
        assert company.name == company_data.name
        assert company.description == company_data.description
        assert company.owner_id == test_user.id
        assert company.visibility is True
        assert company.created_at is not None
        assert company.updated_at is not None

    async def test_get_company_by_id_success(self, uow, test_user):
        company_data = CompanyCreate(
            name="Beta LLC", description="Another company", visibility=False
        )
        created = await company_service.create_company(uow, test_user.id, company_data)
        fetched = await company_service.get_company_by_id(uow, created.id)

        assert fetched.id == created.id
        assert fetched.name == created.name
        assert fetched.description == created.description

    async def test_get_company_by_id_not_found(self, uow):
        with pytest.raises(CompanyNotFoundException):
            await company_service.get_company_by_id(uow, uuid4())

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
        assert result.total == 2
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

        result_page1 = await company_service.read_all_companies(uow, offset=0, limit=1)
        result_page2 = await company_service.read_all_companies(uow, offset=1, limit=1)

        assert result_page1.total == 2
        assert len(result_page1.companies) == 1
        assert result_page2.total == 2
        assert len(result_page2.companies) == 1
        assert result_page1.companies[0].id != result_page2.companies[0].id

    async def test_update_company_success(self, uow, test_user):
        company = await company_service.create_company(
            uow,
            test_user.id,
            CompanyCreate(name="Original", description="Orig Desc", visibility=True),
        )

        update_data = CompanyUpdateRequest(
            name="Updated", description="Updated Desc", visibility=False
        )
        updated = await company_service.update_company(
            uow, company.id, test_user.id, update_data
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

        update_data = CompanyUpdateRequest(name="Updated Only Name")
        updated = await company_service.update_company(
            uow, company.id, test_user.id, update_data
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
        update_data = CompanyUpdateRequest(name="Hacked")

        with pytest.raises(UnauthorizedUserActionException):
            await company_service.update_company(
                uow, company.id, other_user_id, update_data
            )

    async def test_update_company_not_found(self, uow, test_user):
        update_data = CompanyUpdateRequest(name="Updated")

        with pytest.raises(CompanyNotFoundException):
            await company_service.update_company(
                uow, uuid4(), test_user.id, update_data
            )

    async def test_delete_company_success(self, uow, test_user):
        company = await company_service.create_company(
            uow,
            test_user.id,
            CompanyCreate(
                name="ToDelete", description="Will be deleted", visibility=True
            ),
        )

        deleted_company = await company_service.delete_company(
            uow, company.id, test_user.id
        )

        assert deleted_company.id == company.id
        assert deleted_company.name == company.name

        with pytest.raises(CompanyNotFoundException):
            await company_service.get_company_by_id(uow, company.id)

    async def test_delete_company_unauthorized(self, uow, test_user):
        company = await company_service.create_company(
            uow,
            test_user.id,
            CompanyCreate(
                name="ToDelete", description="Will be deleted", visibility=True
            ),
        )

        other_user_id = uuid4()

        with pytest.raises(UnauthorizedUserActionException):
            await company_service.delete_company(uow, company.id, other_user_id)

    async def test_delete_company_not_found(self, uow, test_user):
        with pytest.raises(CompanyNotFoundException):
            await company_service.delete_company(uow, uuid4(), test_user.id)
