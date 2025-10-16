import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.auth_service import AuthService
from app.services.refresh_token_service import RefreshTokenService
from app.services.user_service import UserService
from app.utils.access_token_util import AccessTokenUtil
from app.utils.password_util import PasswordUtil
from app.dependencies.auth0_dependency import Auth0Dependency
from app.exceptions.auth_exceptions import InvalidRefreshTokenWhileGenerating
from tests.factories import make_user


@pytest.fixture
def access_token_util():
    return AccessTokenUtil()


@pytest.fixture
def refresh_token_service():
    service = MagicMock(spec=RefreshTokenService)
    service.create_refresh_token = AsyncMock(return_value="refresh_token_123")
    service.verify_refresh_token = AsyncMock()
    service.rotate_refresh_token = AsyncMock(return_value="new_refresh_token")
    service.revoke_refresh_token = AsyncMock()
    return service


@pytest.fixture
def user_service():
    service = MagicMock(spec=UserService)
    service.get_user_by_email = AsyncMock()
    service.get_user_by_id = AsyncMock()
    service.create_user = AsyncMock()
    return service


@pytest.fixture
def password_util():
    util = MagicMock(spec=PasswordUtil)
    util.verify_password = MagicMock(return_value=True)
    return util


@pytest.fixture
def auth0_dependency():
    return MagicMock(spec=Auth0Dependency)


@pytest.fixture
def auth_service(access_token_util, refresh_token_service, user_service, password_util):
    return AuthService(
        access_token_util,
        refresh_token_service,
        user_service,
        password_util,
    )


@pytest.mark.asyncio
async def test_login_success(mock_uow, auth_service, user_service):
    user = make_user()
    email = user.email
    password = "correct_password"

    user_service.get_user_by_email.return_value = user
    result = await auth_service.login(mock_uow, email, password)

    assert result.access_token is not None
    assert result.refresh_token == "refresh_token_123"
    assert result.token_type == "bearer"
    assert result.expires_in > 0


@pytest.mark.asyncio
async def test_login_invalid_email(mock_uow, auth_service, user_service):
    email = "nonexistent@example.com"
    password = "password"

    user_service.get_user_by_email.return_value = None
    result = await auth_service.login(mock_uow, email, password)

    assert result is None


@pytest.mark.asyncio
async def test_login_invalid_password(
    mock_uow, auth_service, password_util, user_service
):
    user = make_user()
    email = user.email
    password = "wrong_password"
    password_util.verify_password.return_value = False

    user_service.get_user_by_email.return_value = user
    result = await auth_service.login(mock_uow, email, password)

    assert result is None


@pytest.mark.asyncio
async def test_refresh_success(mock_uow, auth_service, refresh_token_service):
    old_token = "old_refresh_token"
    mock_token_obj = MagicMock()
    mock_token_obj.user_id = uuid4()

    refresh_token_service.verify_refresh_token.return_value = mock_token_obj

    result = await auth_service.refresh(mock_uow, old_token)

    assert result.access_token is not None
    assert result.refresh_token == "new_refresh_token"
    assert result.token_type == "bearer"
    refresh_token_service.rotate_refresh_token.assert_called_once()


@pytest.mark.asyncio
async def test_refresh_invalid_token(mock_uow, auth_service, refresh_token_service):
    old_token = "invalid_token"
    refresh_token_service.verify_refresh_token.return_value = None

    with pytest.raises(InvalidRefreshTokenWhileGenerating):
        await auth_service.refresh(mock_uow, old_token)


@pytest.mark.asyncio
async def test_logout_success(mock_uow, auth_service, refresh_token_service):
    refresh_token = "valid_refresh_token"

    await auth_service.logout(mock_uow, refresh_token)

    refresh_token_service.revoke_refresh_token.assert_called_once_with(
        mock_uow, refresh_token
    )
