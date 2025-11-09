from tests.factories.company import CompanyUpdateFactory
from tests.fixtures import *


@pytest.mark.asyncio
async def test_create_company_success(uow, company_service, user_1, company_1_create):
    company = await company_service.create_company(uow, user_1.id, company_1_create)
    assert company.id is not None
    assert company.owner.id == user_1.id
    assert company.visibility is True


@pytest.mark.asyncio
async def test_read_company_by_id_success(uow, company_service, user_1, company_1):
    company = await company_service.read_company_by_id(uow, company_1.id)
    assert company.id == company_1.id
    assert company.owner.id == user_1.id


@pytest.mark.asyncio
async def test_update_company_success(uow, company_service, user_1, company_1):
    updated_data = CompanyUpdateFactory.build(name="New Company Name")
    updated_company = await company_service.update_company(
        uow, company_1.id, updated_data, current_user_id=user_1.id
    )
    assert updated_company.id == company_1.id


@pytest.mark.asyncio
async def test_delete_company_success(uow, company_service, user_1, company_1):
    await company_service.delete_company(uow, company_1.id, current_user_id=user_1.id)
    deleted = await company_service.read_company_by_id(uow, company_1.id)
    assert deleted is None
