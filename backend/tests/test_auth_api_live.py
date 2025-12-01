"""Live server tests for authentication API endpoints."""

import time
import pytest
from httpx import AsyncClient


class TestAuthAPILive:
    """Live server test suite for authentication API endpoints."""

    @pytest.fixture
    def live_client(self):
        """Create HTTP client for live server testing."""
        # Adjust base_url to match your running server
        return AsyncClient(base_url="http://localhost:8000", timeout=30.0)

    def _generate_unique_email(self, prefix: str = "test") -> str:
        """Generate unique email using timestamp to avoid duplicates."""
        timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
        return f"{prefix}_{timestamp}@example.com"

    def _generate_unique_user_data(self, prefix: str = "test"):
        """Generate unique test user data."""
        email = self._generate_unique_email(prefix)
        return {
            "email": email,
            "password": "SecurePass123!",
            "full_name": f"Test User {prefix}"
        }

    @pytest.mark.asyncio
    async def test_register_user_success(self, live_client: AsyncClient):
        """Test successful user registration on live server."""
        user_data = self._generate_unique_user_data("register_success")

        response = await live_client.post("/api/v1/auth/register", json=user_data)

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
        assert user["email"] == user_data["email"]
        assert user["full_name"] == user_data["full_name"]
        assert user["id"] is not None
        assert user["created_at"] is not None

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, live_client: AsyncClient):
        """Test registration with duplicate email fails on live server."""
        user_data = self._generate_unique_user_data("duplicate")

        # First registration
        response1 = await live_client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201

        # Second registration with same email
        response2 = await live_client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 409
        data = response2.json()
        assert "already exists" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_weak_password(self, live_client: AsyncClient):
        """Test registration with weak password fails on live server."""
        user_data = self._generate_unique_user_data("weak")
        user_data["password"] = "123"  # Weak password

        response = await live_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "password" in str(data).lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, live_client: AsyncClient):
        """Test registration with invalid email fails on live server."""
        user_data = {
            "email": "invalid-email",
            "password": "SecurePass123!",
            "full_name": "Invalid Email User"
        }

        response = await live_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "email" in str(data).lower()

    @pytest.mark.asyncio
    async def test_login_success(self, live_client: AsyncClient):
        """Test successful user login on live server."""
        user_data = self._generate_unique_user_data("login")

        # First register the user
        register_response = await live_client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201

        # Then login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        response = await live_client.post("/api/v1/auth/login", json=login_data)

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
        assert user["email"] == user_data["email"]
        assert user["full_name"] == user_data["full_name"]

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, live_client: AsyncClient):
        """Test login with wrong password fails on live server."""
        user_data = self._generate_unique_user_data("wrong_pass")

        # First register the user
        register_response = await live_client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201

        # Try login with wrong password
        login_data = {
            "email": user_data["email"],
            "password": "wrongpassword"
        }
        response = await live_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "invalid credentials" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, live_client: AsyncClient):
        """Test login with nonexistent user fails on live server."""
        login_data = {
            "email": self._generate_unique_email("nonexistent"),
            "password": "somepassword"
        }
        response = await live_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "invalid credentials" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_current_user_profile(self, live_client: AsyncClient):
        """Test getting current user profile on live server."""
        user_data = self._generate_unique_user_data("profile")

        # Register and login user
        register_response = await live_client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        tokens = register_response.json()

        # Get user profile
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = await live_client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Check user data
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert data["is_active"] is True
        assert data["is_verified"] is False  # Default value
        assert data["id"] is not None
        assert data["created_at"] is not None

    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, live_client: AsyncClient):
        """Test getting user profile without authentication fails on live server."""
        response = await live_client.get("/api/v1/auth/me")
        assert response.status_code == 403  # Forbidden by HTTPBearer

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, live_client: AsyncClient):
        """Test successful token refresh on live server."""
        user_data = self._generate_unique_user_data("refresh")

        # Register and login user
        register_response = await live_client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        tokens = register_response.json()

        # Refresh token
        refresh_data = {"refresh_token": tokens["refresh_token"]}
        response = await live_client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"
        assert data["expires_in"] == 3600

        # Verify tokens are present and valid
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, live_client: AsyncClient):
        """Test refresh with invalid token fails on live server."""
        refresh_data = {"refresh_token": "invalid-refresh-token"}
        response = await live_client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == 401
        data = response.json()
        assert "invalid refresh token" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_change_password_success(self, live_client: AsyncClient):
        """Test successful password change on live server."""
        user_data = self._generate_unique_user_data("change_pass")

        # First register user
        register_response = await live_client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        access_token = register_response.json()["access_token"]

        # Change password
        change_data = {
            "current_password": user_data["password"],
            "new_password": "NewSecurePass456!"
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await live_client.post("/api/v1/auth/change-password", json=change_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "changed successfully" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, live_client: AsyncClient):
        """Test password change with wrong current password fails on live server."""
        user_data = self._generate_unique_user_data("wrong_current")

        # First register user
        register_response = await live_client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        access_token = register_response.json()["access_token"]

        # Try to change password with wrong current password
        change_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewSecurePass456!"
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await live_client.post("/api/v1/auth/change-password", json=change_data, headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_forgot_password_success(self, live_client: AsyncClient):
        """Test successful forgot password request on live server."""
        forgot_data = {"email": self._generate_unique_email("forgot")}
        response = await live_client.post("/api/v1/auth/forgot-password", json=forgot_data)
        assert response.status_code == 200
        data = response.json()
        assert "reset link" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_forgot_password_invalid_email(self, live_client: AsyncClient):
        """Test forgot password with invalid email fails on live server."""
        forgot_data = {"email": "invalid-email"}
        response = await live_client.post("/api/v1/auth/forgot-password", json=forgot_data)
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "email" in str(data).lower()

    @pytest.mark.asyncio
    async def test_reset_password_success(self, live_client: AsyncClient):
        """Test successful password reset on live server."""
        reset_data = {
            "token": f"reset_token_{int(time.time())}",
            "new_password": "NewSecurePass456!"
        }
        response = await live_client.post("/api/v1/auth/reset-password", json=reset_data)
        assert response.status_code == 200
        data = response.json()
        assert "reset successfully" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_reset_password_invalid_token(self, live_client: AsyncClient):
        """Test password reset with invalid token fails on live server."""
        reset_data = {
            "token": "short",
            "new_password": "NewSecurePass456!"
        }
        response = await live_client.post("/api/v1/auth/reset-password", json=reset_data)
        assert response.status_code == 422
        data = response.json()
        assert "token" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_health_check(self, live_client: AsyncClient):
        """Test health check endpoint on live server."""
        response = await live_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"