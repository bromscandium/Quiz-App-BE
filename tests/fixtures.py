import pytest_asyncio

from app.schemas.user import UserCreate
from app.services.user import UserService
from app.services.company import CompanyService
from app.schemas.company import CompanyCreate
from app.unit_of_work.uow import UnitOfWork


@pytest_asyncio.fixture
async def test_user(async_session_factory):
    user_service = UserService()
    user_data = UserCreate(
        name="testname",
        email="testuser@example.com",
        nickname="testuser",
        password="Test@1234",
    )

    async with UnitOfWork(async_session_factory) as uow:
        user = await user_service.create_user(uow, user_data)
        await uow.commit()
        return user


@pytest_asyncio.fixture
async def test_second_user(async_session_factory):
    user_service = UserService()
    user_data = UserCreate(
        name="testname2",
        email="testuser2@example.com",
        nickname="testuser2",
        password="Test@1234",
    )

    async with UnitOfWork(async_session_factory) as uow:
        user = await user_service.create_user(uow, user_data)
        await uow.commit()
        return user


@pytest_asyncio.fixture
async def test_company(async_session_factory, test_user):
    company_service = CompanyService()
    company_data = CompanyCreate(name="Test Company", visibility=True)

    async with UnitOfWork(async_session_factory) as uow:
        company = await company_service.create_company(uow, test_user.id, company_data)
        await uow.commit()
        return company
