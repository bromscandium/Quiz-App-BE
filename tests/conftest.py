import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(autouse=True)
def mock_dependencies():
    mock_session = MagicMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(return_value=None)
    mock_session.rollback = AsyncMock()

    async def mock_get_session():
        yield mock_session

    mock_redis = MagicMock()
    mock_redis.ping = AsyncMock(return_value=True)

    with (
        patch(
            "app.db.postgres.sessionmanager.get_session",
            return_value=mock_get_session(),
        ),
        patch("app.db.redis.RedisClient.redis_client", mock_redis),
    ):
        yield
