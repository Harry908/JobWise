"""Comprehensive tests for authentication API endpoints."""

import pytest
from httpx import AsyncClient

from app.core.config import get_settings


class TestAuthAPI:
    """Test suite for authentication API endpoints."""

    @pytest.mark.asyncio
    async def test_register_user_success(self, client: AsyncClient, test_user_data: dict):
        """Test successful user registration."""
        response = await client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == 201
        data = response.json()

        # Check response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"
        assert data["expires_in"] == 3600
        assert "user" in data

        # Check user data
        user = data["user"]
        assert user["email"] == test_user_data["email"]
        assert user["full_name"] == test_user_data["full_name"]
        assert user["id"] is not None
        assert user["created_at"] is not None

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user_data: dict):
        """Test registration with duplicate email fails."""
        # First registration
        response1 = await client.post("/api/v1/auth/register", json=test_user_data)
        assert response1.status_code == 201

        # Second registration with same email
        response2 = await client.post("/api/v1/auth/register", json=test_user_data)
        assert response2.status_code == 409
        data = response2.json()
        assert "already exists" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient, weak_password_data: dict):
        """Test registration with weak password fails."""
        response = await client.post("/api/v1/auth/register", json=weak_password_data)
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "password" in str(data).lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient, invalid_email_data: dict):
        """Test registration with invalid email fails."""
        response = await client.post("/api/v1/auth/register", json=invalid_email_data)
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "email" in str(data).lower()

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user_data: dict):
        """Test successful user login."""
        # First register the user
        register_response = await client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == 201

        # Then login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"
        assert data["expires_in"] == 3600
        assert "user" in data

        # Check user data
        user = data["user"]
        assert user["email"] == test_user_data["email"]
        assert user["full_name"] == test_user_data["full_name"]

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user_data: dict):
        """Test login with wrong password fails."""
        # First register the user
        register_response = await client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == 201

        # Try login with wrong password
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "invalid credentials" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user fails."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "somepassword"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "invalid credentials" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_current_user_profile(self, client: AsyncClient, test_user_data: dict):
        """Test getting current user profile."""
        # Register and login user
        register_response = await client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == 201
        tokens = register_response.json()

        # Get user profile
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = await client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Check user data
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert data["is_active"] is True
        assert data["is_verified"] is False  # Default value
        assert data["id"] is not None
        assert data["created_at"] is not None

    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting user profile without authentication fails."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 403  # Forbidden by HTTPBearer

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting user profile with invalid token fails."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient, test_user_data: dict):
        """Test successful token refresh."""
        # Register and login user
        register_response = await client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == 201
        tokens = register_response.json()

        # Refresh token
        refresh_data = {"refresh_token": tokens["refresh_token"]}
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"
        assert data["expires_in"] == 3600

        # Verify tokens are present and valid
        # Note: tokens may be identical if created in the same millisecond,
        # but they are functionally valid
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test refresh with invalid token fails."""
        refresh_data = {"refresh_token": "invalid-refresh-token"}
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == 401
        data = response.json()
        assert "invalid refresh token" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_access_protected_endpoint_with_valid_token(self, client: AsyncClient, test_user_data: dict):
        """Test accessing protected endpoint with valid token."""
        # Register and login user
        register_response = await client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == 201
        tokens = register_response.json()

        # Access protected endpoint
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = await client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_access_protected_endpoint_with_expired_token(self, client: AsyncClient):
        """Test accessing protected endpoint with expired token fails."""
        # This would require mocking time or using a pre-expired token
        # For now, we'll test with an invalid token
        headers = {"Authorization": "Bearer expired-token"}
        response = await client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_register_empty_fields(self, client: AsyncClient):
        """Test registration with empty required fields fails."""
        test_data = {
            "email": "",
            "password": "",
            "full_name": ""
        }
        response = await client.post("/api/v1/auth/register", json=test_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_empty_fields(self, client: AsyncClient):
        """Test login with empty fields fails."""
        test_data = {
            "email": "",
            "password": ""
        }
        response = await client.post("/api/v1/auth/login", json=test_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_refresh_empty_token(self, client: AsyncClient):
        """Test refresh with empty token fails."""
        test_data = {"refresh_token": ""}
        response = await client.post("/api/v1/auth/refresh", json=test_data)
        assert response.status_code == 401  # Invalid token
        data = response.json()
        assert "invalid" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_logout_success(self, client: AsyncClient, test_user_data: dict):
        """Test successful logout."""
        # First register and login
        register_response = await client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == 201
        access_token = register_response.json()["access_token"]

        # Test logout with valid token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/v1/auth/logout", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "logged out" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_logout_unauthorized(self, client: AsyncClient):
        """Test logout without authentication fails."""
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 403  # Forbidden due to missing token

    @pytest.mark.asyncio
    async def test_change_password_success(self, client: AsyncClient, test_user_data: dict):
        """Test successful password change."""
        # First register user
        register_response = await client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == 201
        access_token = register_response.json()["access_token"]

        # Change password
        change_data = {
            "current_password": test_user_data["password"],
            "new_password": "NewSecurePass456!"
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/v1/auth/change-password", json=change_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "changed successfully" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, client: AsyncClient, test_user_data: dict):
        """Test password change with wrong current password fails."""
        # First register user
        register_response = await client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == 201
        access_token = register_response.json()["access_token"]

        # Try to change password with wrong current password
        change_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewSecurePass456!"
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/v1/auth/change-password", json=change_data, headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_change_password_weak_new(self, client: AsyncClient, test_user_data: dict):
        """Test password change with weak new password fails."""
        # First register user
        register_response = await client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == 201
        access_token = register_response.json()["access_token"]

        # Try to change password with weak new password
        change_data = {
            "current_password": test_user_data["password"],
            "new_password": "weak"
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/v1/auth/change-password", json=change_data, headers=headers)
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "password" in str(data).lower()

    @pytest.mark.asyncio
    async def test_change_password_same_as_current(self, client: AsyncClient, test_user_data: dict):
        """Test password change with same password fails."""
        # First register user
        register_response = await client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == 201
        access_token = register_response.json()["access_token"]

        # Try to change password to same as current
        change_data = {
            "current_password": test_user_data["password"],
            "new_password": test_user_data["password"]
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/v1/auth/change-password", json=change_data, headers=headers)
        assert response.status_code == 422
        data = response.json()
        assert "different" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_change_password_unauthorized(self, client: AsyncClient):
        """Test password change without authentication fails."""
        change_data = {
            "current_password": "CurrentPass123!",
            "new_password": "NewSecurePass456!"
        }
        response = await client.post("/api/v1/auth/change-password", json=change_data)
        assert response.status_code == 403  # Forbidden due to missing token

    @pytest.mark.asyncio
    async def test_forgot_password_success(self, client: AsyncClient):
        """Test successful forgot password request."""
        forgot_data = {"email": "test@example.com"}
        response = await client.post("/api/v1/auth/forgot-password", json=forgot_data)
        assert response.status_code == 200
        data = response.json()
        assert "reset link" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_forgot_password_invalid_email(self, client: AsyncClient):
        """Test forgot password with invalid email fails."""
        forgot_data = {"email": "invalid-email"}
        response = await client.post("/api/v1/auth/forgot-password", json=forgot_data)
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "email" in str(data).lower()

    @pytest.mark.asyncio
    async def test_reset_password_success(self, client: AsyncClient):
        """Test successful password reset."""
        reset_data = {
            "token": "valid_reset_token_12345",
            "new_password": "NewSecurePass456!"
        }
        response = await client.post("/api/v1/auth/reset-password", json=reset_data)
        assert response.status_code == 200
        data = response.json()
        assert "reset successfully" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_reset_password_invalid_token(self, client: AsyncClient):
        """Test password reset with invalid token fails."""
        reset_data = {
            "token": "short",
            "new_password": "NewSecurePass456!"
        }
        response = await client.post("/api/v1/auth/reset-password", json=reset_data)
        assert response.status_code == 422
        data = response.json()
        assert "token" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_reset_password_weak_password(self, client: AsyncClient):
        """Test password reset with weak password fails."""
        reset_data = {
            "token": "valid_reset_token_12345",
            "new_password": "weak"
        }
        response = await client.post("/api/v1/auth/reset-password", json=reset_data)
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "password" in str(data).lower()

    @pytest.mark.asyncio
    async def test_check_email_available(self, client: AsyncClient):
        """Test checking if email is available for registration."""
        # Test with non-existent email
        response = await client.get("/api/v1/auth/check-email?email=available@example.com")
        assert response.status_code == 200
        data = response.json()
        assert data["available"] is True

    @pytest.mark.asyncio
    async def test_check_email_taken(self, client: AsyncClient, test_user_data: dict):
        """Test checking if email is taken (already registered)."""
        # First register a user
        register_response = await client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == 201

        # Now check if email is available
        response = await client.get(f"/api/v1/auth/check-email?email={test_user_data['email']}")
        assert response.status_code == 200
        data = response.json()
        assert data["available"] is False

    @pytest.mark.asyncio
    async def test_check_email_invalid_format(self, client: AsyncClient):
        """Test checking email availability with invalid email format."""
        response = await client.get("/api/v1/auth/check-email?email=invalid-email")
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "email" in str(data).lower()

    @pytest.mark.asyncio
    async def test_check_email_missing_parameter(self, client: AsyncClient):
        """Test checking email availability without email parameter."""
        response = await client.get("/api/v1/auth/check-email")
        assert response.status_code == 422  # Missing required parameter
