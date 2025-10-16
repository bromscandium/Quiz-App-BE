import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest_asyncio.fixture
def mock_user_repo():
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.read_by = AsyncMock(return_value=None)
    repo.read_all = AsyncMock(return_value=[])
    repo.update_by = AsyncMock()
    repo.delete_by = AsyncMock()
    return repo


@pytest_asyncio.fixture
def mock_refresh_token_repo():
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.read_by = AsyncMock(return_value=None)
    repo.update_by = AsyncMock()
    repo.delete_by = AsyncMock()
    return repo


@pytest_asyncio.fixture
def mock_uow(mock_user_repo, mock_refresh_token_repo):
    uow = AsyncMock()
    uow.users = mock_user_repo
    uow.refresh_tokens = mock_refresh_token_repo
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow


@pytest_asyncio.fixture()
def mock_redis():
    redis = AsyncMock()
    with patch("app.db.redis.RedisClient.redis_client", new=redis):
        yield redis


@pytest_asyncio.fixture
async def client():
    with patch("app.dependencies.auth0_dependency.Auth0Dependency"):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac
