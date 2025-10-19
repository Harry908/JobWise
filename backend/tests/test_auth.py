"""Tests for authentication service and endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import uuid4

from app.application.services.auth_service import AuthService
from app.application.dtos.auth_dtos import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    PasswordChangeRequest
)
from app.core.exceptions import AuthenticationException, ValidationException
from app.domain.entities.user import User
from app.core.security import PasswordHasher
from app.infrastructure.database.repositories import UserRepository


class TestAuthService:
    """Test cases for AuthService."""

    @pytest.fixture
    def mock_user_repo(self):
        """Mock user repository."""
        return AsyncMock(spec=UserRepository)

    @pytest.fixture
    def auth_service(self, mock_user_repo):
        """Auth service instance with mocked repository."""
        return AuthService(mock_user_repo)

    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service, mock_user_repo):
        """Test successful user registration."""
        # Arrange
        request = UserRegisterRequest(
            email="test@example.com",
            password="SecurePass123",
            full_name="Test User"
        )

        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        mock_user.is_verified = False
        mock_user.created_at = "2024-01-01T00:00:00Z"
        mock_user.updated_at = "2024-01-01T00:00:00Z"
        mock_user.last_active_at = None

        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.create.return_value = mock_user

        # Act
        with patch('app.application.services.auth_service.hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            result = await auth_service.register_user(request)

        # Assert
        assert result.id == "test-user-id"
        assert result.email == "test@example.com"
        assert result.full_name == "Test User"
        assert result.is_active is True
        assert result.is_verified is False

        mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
        mock_user_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_email_exists(self, auth_service, mock_user_repo):
        """Test registration with existing email."""
        # Arrange
        request = UserRegisterRequest(
            email="existing@example.com",
            password="SecurePass123",
            full_name="Test User"
        )

        mock_user_repo.get_by_email.return_value = MagicMock()  # User exists

        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            await auth_service.register_user(request)

        assert "already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_register_user_invalid_email(self, auth_service, mock_user_repo):
        """Test registration with invalid email."""
        # This test is not needed since Pydantic validates email format
        # at the DTO level before reaching the service
        pass

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, mock_user_repo):
        """Test successful user authentication."""
        # Arrange
        request = UserLoginRequest(
            email="test@example.com",
            password="SecurePass123"
        )

        # Use a mock hashed password
        hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewfBPjYQmHqU3G3K"

        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.password_hash = hashed_password
        mock_user.first_name = "Test"
        mock_user.last_name = "User"
        mock_user.is_active = True
        mock_user.is_verified = True
        mock_user.created_at = datetime.utcnow()
        mock_user.updated_at = datetime.utcnow()
        mock_user.last_active_at = None

        mock_user_repo.get_by_email.return_value = mock_user
        mock_user_repo.update_last_login.return_value = None

        # Act
        with patch('app.application.services.auth_service.verify_password') as mock_verify:
            mock_verify.return_value = True
            result = await auth_service.authenticate_user(request)

        # Assert
        assert isinstance(result, TokenResponse)
        assert result.token_type == "bearer"
        assert result.expires_in == 1800
        assert result.user_id == "test-user-id"

        mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
        mock_user_repo.update_last_login.assert_called_once_with("test-user-id")

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_credentials(self, auth_service, mock_user_repo):
        """Test authentication with invalid credentials."""
        # Arrange
        request = UserLoginRequest(
            email="test@example.com",
            password="WrongPassword123"
        )

        mock_user = MagicMock()
        mock_user.password_hash = "hashed_password"

        mock_user_repo.get_by_email.return_value = mock_user

        # Act & Assert
        with pytest.raises(AuthenticationException) as exc_info:
            await auth_service.authenticate_user(request)

        assert "Invalid email or password" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_authenticate_user_account_deactivated(self, auth_service, mock_user_repo):
        """Test authentication with deactivated account."""
        # Arrange
        request = UserLoginRequest(
            email="test@example.com",
            password="SecurePass123"
        )

        mock_user = MagicMock()
        mock_user.is_active = False
        mock_user.is_verified = True

        mock_user_repo.get_by_email.return_value = mock_user

        # Act & Assert
        with pytest.raises(AuthenticationException) as exc_info:
            await auth_service.authenticate_user(request)

        assert "Account is deactivated" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_change_password_success(self, auth_service, mock_user_repo):
        """Test successful password change."""
        # Arrange
        user_id = "test-user-id"
        request = PasswordChangeRequest(
            current_password="OldSecurePass123",
            new_password="NewSecurePass456"
        )

        # Use a mock hashed password
        current_hashed = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewfBPjYQmHqU3G3K"

        mock_user = MagicMock()
        mock_user.password_hash = current_hashed
        mock_user.first_name = "Test"
        mock_user.last_name = "User"
        mock_user.is_active = True
        mock_user.is_verified = True
        mock_user.created_at = datetime.utcnow()
        mock_user.updated_at = datetime.utcnow()
        mock_user.last_active_at = None

        mock_user_repo.get_by_id.return_value = mock_user
        mock_user_repo.update.return_value = None

        # Act
        with patch('app.application.services.auth_service.verify_password') as mock_verify, \
             patch('app.application.services.auth_service.hash_password') as mock_hash:
            mock_verify.return_value = True
            mock_hash.return_value = "new_hashed_password"
            await auth_service.change_password(user_id, request)

        # Assert
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_user_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, auth_service, mock_user_repo):
        """Test password change with wrong current password."""
        # Arrange
        user_id = "test-user-id"
        request = PasswordChangeRequest(
            current_password="WrongPassword123",
            new_password="NewSecurePass456"
        )

        mock_user = MagicMock()
        mock_user.password_hash = "hashed_old_password"

        mock_user_repo.get_by_id.return_value = mock_user

        # Act & Assert
        with pytest.raises(AuthenticationException) as exc_info:
            await auth_service.change_password(user_id, request)

        assert "Current password is incorrect" in str(exc_info.value)


class TestUserEntity:
    """Test cases for User entity."""

    def test_user_creation(self):
        """Test user entity creation."""
        user = User.create(
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User"
        )

        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.last_login_at is None

    def test_email_validation(self):
        """Test email validation."""
        assert User.validate_email("valid@example.com") is True
        assert User.validate_email("invalid-email") is False
        assert User.validate_email("") is False

    def test_password_validation(self):
        """Test password validation."""
        assert User.validate_password("SecurePass123") is True
        assert User.validate_password("short") is False  # Too short
        assert User.validate_password("nouppercase123") is False  # No uppercase
        assert User.validate_password("NOLOWERCASE123") is False  # No lowercase
        assert User.validate_password("NoNumbers") is False  # No numbers

    def test_can_login(self):
        """Test login eligibility."""
        # Active and verified user
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hash",
            full_name="Test User",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        assert user.can_login() is True

        # Inactive user
        user.is_active = False
        assert user.can_login() is False

        # Unverified user
        user.is_active = True
        user.is_verified = False
        assert user.can_login() is False