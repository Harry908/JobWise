import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from app.application.services.auth_service import AuthService
from app.core.security import JWTManager, PasswordHasher
from app.core.exceptions import AuthenticationException, NotFoundError, ValidationException
from app.application.dtos.auth_dtos import RefreshTokenRequest, PasswordChangeRequest
from app.infrastructure.database.repositories import UserRepository


@pytest.mark.asyncio
async def test_refresh_access_token_invalid_token(mock_user_repo=None):
    # Arrange
    mock_repo = AsyncMock(spec=UserRepository)
    auth_service = AuthService(mock_repo)

    # Use an invalid token string
    request = RefreshTokenRequest(refresh_token="invalid.token")

    # Patch get_user_id_from_token to raise AuthenticationException
    with patch('app.application.services.auth_service.get_user_id_from_token') as mock_get_user_id:
        mock_get_user_id.side_effect = AuthenticationException("Invalid refresh token")
        with pytest.raises(AuthenticationException):
            await auth_service.refresh_access_token(request)


@pytest.mark.asyncio
async def test_refresh_access_token_user_not_found():
    # Arrange
    mock_repo = AsyncMock(spec=UserRepository)
    auth_service = AuthService(mock_repo)

    # Create a valid-looking token by patching get_user_id_from_token
    request = RefreshTokenRequest(refresh_token="valid.token")

    with patch('app.application.services.auth_service.get_user_id_from_token') as mock_get_user_id:
        mock_get_user_id.return_value = "nonexistent-user"
        mock_repo.get_by_id.return_value = None

        with pytest.raises(AuthenticationException):
            await auth_service.refresh_access_token(request)


@pytest.mark.asyncio
async def test_get_current_user_not_found():
    mock_repo = AsyncMock(spec=UserRepository)
    auth_service = AuthService(mock_repo)

    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await auth_service.get_current_user("no-user")


@pytest.mark.asyncio
async def test_change_password_user_not_found():
    mock_repo = AsyncMock(spec=UserRepository)
    auth_service = AuthService(mock_repo)

    mock_repo.get_by_id.return_value = None

    request = PasswordChangeRequest(current_password="a", new_password="NewPass123")
    with pytest.raises(NotFoundError):
        await auth_service.change_password("no-user", request)


@pytest.mark.asyncio
async def test_verify_user_account_already_verified():
    mock_repo = AsyncMock(spec=UserRepository)
    auth_service = AuthService(mock_repo)

    mock_user = MagicMock()
    mock_user.is_verified = True
    mock_repo.get_by_id.return_value = mock_user

    with pytest.raises(ValidationException):
        await auth_service.verify_user_account("some-user")


@pytest.mark.asyncio
async def test_deactivate_activate_user_not_found():
    mock_repo = AsyncMock(spec=UserRepository)
    auth_service = AuthService(mock_repo)

    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await auth_service.deactivate_user_account("no-user")

    with pytest.raises(NotFoundError):
        await auth_service.activate_user_account("no-user")


def test_password_hasher_empty_password_raises():
    with pytest.raises(Exception):
        PasswordHasher.hash_password("")


def test_jwt_token_expiry_and_verification(monkeypatch):
    # Create a short-lived token and ensure expiry is detected
    user_id = "test-user"

    token = JWTManager.create_access_token(user_id, expires_delta=timedelta(seconds=1))

    # Immediately verify should pass
    td = JWTManager.verify_token(token)
    assert td.user_id == user_id

    # Simulate expiry by creating a token with negative expiry
    expired_token = JWTManager.create_access_token(user_id, expires_delta=timedelta(seconds=-1))
    with pytest.raises(AuthenticationException):
        JWTManager.verify_token(expired_token)
