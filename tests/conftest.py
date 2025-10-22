import asyncio

import asyncpg
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.models import Base
from app.schemas.user_schema import SignUpRequest
from app.services.user_service import UserService
from app.unit_of_work.uow import UnitOfWork
from tests.core.test_db_settings import DbSettings

db_settings = DbSettings()


async def _wait_for_postgres(retries=5, delay=1):
    for _ in range(retries):
        try:
            conn = await asyncpg.connect(
                host=db_settings.host,
                port=db_settings.port,
                user=db_settings.user,
                password=db_settings.password,
                database=db_settings.db,
            )
            await conn.close()
            return
        except Exception:
            await asyncio.sleep(delay)
    raise ConnectionError("Cannot connect to Postgres")


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    await _wait_for_postgres()
    engine = create_async_engine(
        db_settings.url,
        echo=False,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session_factory(test_engine):
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def test_user(async_session_factory):
    user_service = UserService()
    user_data = SignUpRequest(
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
async def uow(async_session_factory):
    async with UnitOfWork(async_session_factory) as uow:
        yield uow


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
