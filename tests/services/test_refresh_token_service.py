import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.services.refresh_token_service import RefreshTokenService
from app.exceptions.refresh_token_exceptions import (
    InvalidRefreshTokenException,
    NotFoundRefreshToken,
)
from app.utils.refresh_token_util import RefreshTokenUtil


@pytest.fixture
def refresh_token_util():
    return RefreshTokenUtil()


@pytest.fixture
def refresh_token_service(refresh_token_util):
    return RefreshTokenService(refresh_token_util)


@pytest.fixture
def mock_token_obj():
    token = MagicMock()
    token.id = uuid4()
    token.user_id = uuid4()
    token.token_hash = "hashed_token"
    token.expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    token.revoked = False
    return token


@pytest.mark.asyncio
async def test_create_refresh_token_success(mock_uow, refresh_token_service):
    user_id = uuid4()
    mock_uow.refresh_tokens.create = AsyncMock(return_value=None)
    mock_uow.commit = AsyncMock()

    token = await refresh_token_service.create_refresh_token(mock_uow, user_id)

    assert isinstance(token, str)
    assert len(token) > 0
    mock_uow.refresh_tokens.create.assert_called_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_verify_refresh_token_success(
    mock_uow, refresh_token_service, mock_token_obj
):
    raw_token = "test_raw_token"
    mock_uow.refresh_tokens.read_by = AsyncMock(return_value=mock_token_obj)

    result = await refresh_token_service.verify_refresh_token(mock_uow, raw_token)

    assert result == mock_token_obj
    assert result.revoked is False


@pytest.mark.asyncio
async def test_verify_refresh_token_not_found(mock_uow, refresh_token_service):
    raw_token = "invalid_token"
    mock_uow.refresh_tokens.read_by = AsyncMock(return_value=None)

    result = await refresh_token_service.verify_refresh_token(mock_uow, raw_token)

    assert result is None


@pytest.mark.asyncio
async def test_verify_refresh_token_revoked(
    mock_uow, refresh_token_service, mock_token_obj
):
    raw_token = "revoked_token"
    mock_token_obj.revoked = True
    mock_uow.refresh_tokens.read_by = AsyncMock(return_value=mock_token_obj)

    result = await refresh_token_service.verify_refresh_token(mock_uow, raw_token)

    assert result is None


@pytest.mark.asyncio
async def test_verify_refresh_token_expired(
    mock_uow, refresh_token_service, mock_token_obj
):
    raw_token = "expired_token"
    mock_token_obj.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    mock_uow.refresh_tokens.read_by = AsyncMock(return_value=mock_token_obj)

    result = await refresh_token_service.verify_refresh_token(mock_uow, raw_token)

    assert result is None


@pytest.mark.asyncio
async def test_revoke_refresh_token_success(
    mock_uow, refresh_token_service, mock_token_obj
):
    raw_token = "valid_token"
    mock_uow.refresh_tokens.read_by = AsyncMock(return_value=mock_token_obj)
    mock_uow.refresh_tokens.update_by = AsyncMock()
    mock_uow.commit = AsyncMock()

    with patch.object(
        refresh_token_service, "verify_refresh_token", return_value=mock_token_obj
    ):
        await refresh_token_service.revoke_refresh_token(mock_uow, raw_token)

    mock_uow.refresh_tokens.update_by.assert_called_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_revoke_refresh_token_not_found(mock_uow, refresh_token_service):
    raw_token = "invalid_token"

    with patch.object(refresh_token_service, "verify_refresh_token", return_value=None):
        with pytest.raises(NotFoundRefreshToken):
            await refresh_token_service.revoke_refresh_token(mock_uow, raw_token)


@pytest.mark.asyncio
async def test_rotate_refresh_token_success(
    mock_uow, refresh_token_service, mock_token_obj
):
    old_token = "old_token"
    user_id = mock_token_obj.user_id
    new_token = "new_token_value"

    mock_uow.refresh_tokens.update_by = AsyncMock()
    mock_uow.commit = AsyncMock()

    with patch.object(
        refresh_token_service, "verify_refresh_token", return_value=mock_token_obj
    ):
        with patch.object(
            refresh_token_service, "create_refresh_token", return_value=new_token
        ):
            result = await refresh_token_service.rotate_refresh_token(
                mock_uow, old_token, user_id
            )

    assert result == new_token
    mock_uow.refresh_tokens.update_by.assert_called_once()
    mock_uow.commit.assert_called()


@pytest.mark.asyncio
async def test_rotate_refresh_token_invalid_user(
    mock_uow, refresh_token_service, mock_token_obj
):
    old_token = "old_token"
    wrong_user_id = uuid4()
    mock_uow.rollback = AsyncMock()

    with patch.object(
        refresh_token_service, "verify_refresh_token", return_value=mock_token_obj
    ):
        with pytest.raises(InvalidRefreshTokenException):
            await refresh_token_service.rotate_refresh_token(
                mock_uow, old_token, wrong_user_id
            )

    mock_uow.rollback.assert_called_once()
