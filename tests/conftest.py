import pytest_asyncio
import redis.asyncio as redis
from celery import Celery
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.models import Base
from app.unit_of_work import UnitOfWork
from tests.core.app import DbSettings, RedisSettings

db_settings = DbSettings()
redis_settings = RedisSettings()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(
        db_settings.url,
        echo=False,
        pool_pre_ping=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session_factory(test_engine):
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


@pytest_asyncio.fixture
async def uow(async_session_factory):
    async with UnitOfWork(async_session_factory) as uow:
        yield uow
        try:
            await uow.commit()
        except Exception:
            await uow.rollback()


@pytest_asyncio.fixture(scope="function")
async def redis_client():
    client = redis.from_url(redis_settings.url, decode_responses=True)
    await client.ping()

    yield client

    await client.flushdb()
    await client.aclose()


@pytest_asyncio.fixture(scope="function")
def celery_app():
    test_celery_app = Celery(
        "test_quiz_app",
        broker=redis_settings.url,
        backend=redis_settings.url,
        include=["tests.test_tasks.test_quiz"],
    )

    test_celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        task_serializer="json",
        accept_content=["json"],
    )

    yield test_celery_app


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
