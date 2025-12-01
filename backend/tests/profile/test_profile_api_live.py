"""Live server tests for profile API endpoints."""

import time
import pytest
from httpx import AsyncClient


class TestProfileAPILive:
    """Live server test suite for profile API endpoints."""

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

    async def _get_auth_headers(self, live_client: AsyncClient, user_data: dict) -> dict:
        """Helper to register user and get auth headers."""
        # Register user
        register_response = await live_client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        access_token = register_response.json()["access_token"]
        return {"Authorization": f"Bearer {access_token}"}

    def _get_sample_profile_data(self):
        """Get sample profile creation data."""
        return {
            "personal_info": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "phone": "+1-555-123-4567",
                "location": "Seattle, WA",
                "linkedin": "https://linkedin.com/in/johndoe",
                "github": "https://github.com/johndoe",
                "website": "https://johndoe.com"
            },
            "professional_summary": "Experienced software developer with 5+ years in web development, specializing in Python and JavaScript technologies.",
            "skills": {
                "technical": ["Python", "FastAPI", "React", "PostgreSQL"],
                "soft": ["Leadership", "Communication", "Problem Solving"],
                "languages": [
                    {"name": "English", "proficiency": "native"},
                    {"name": "Spanish", "proficiency": "conversational"}
                ],
                "certifications": [
                    {
                        "name": "AWS Solutions Architect",
                        "issuer": "Amazon",
                        "date_obtained": "2023-01-01",
                        "credential_id": "AWS-123"
                    }
                ]
            }
        }

    @pytest.mark.asyncio
    async def test_create_profile_success(self, live_client: AsyncClient):
        """Test successful profile creation on live server."""
        user_data = self._generate_unique_user_data("profile_create")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)

        assert response.status_code == 201
        data = response.json()

        # Check response structure
        assert "id" in data
        assert "user_id" in data
        assert data["personal_info"]["full_name"] == profile_data["personal_info"]["full_name"]
        assert data["professional_summary"] == profile_data["professional_summary"]
        assert len(data["skills"]["technical"]) == len(profile_data["skills"]["technical"])
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_profile_duplicate_user(self, live_client: AsyncClient):
        """Test profile creation fails when user already has a profile."""
        user_data = self._generate_unique_user_data("duplicate_profile")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create first profile
        response1 = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert response1.status_code == 201

        # Try to create second profile
        response2 = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert response2.status_code == 422
        data = response2.json()
        assert "already has a profile" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_profile_invalid_data(self, live_client: AsyncClient):
        """Test profile creation fails with invalid data."""
        user_data = self._generate_unique_user_data("invalid_profile")
        headers = await self._get_auth_headers(live_client, user_data)

        invalid_profile_data = {
            "personal_info": {
                "full_name": "",  # Invalid: empty name
                "email": "invalid-email"  # Invalid: bad email format
            }
        }

        response = await live_client.post("/api/v1/profiles", json=invalid_profile_data, headers=headers)
        assert response.status_code == 422  # Pydantic validation error

    @pytest.mark.asyncio
    async def test_create_profile_unauthorized(self, live_client: AsyncClient):
        """Test profile creation fails without authentication."""
        profile_data = self._get_sample_profile_data()

        response = await live_client.post("/api/v1/profiles", json=profile_data)
        assert response.status_code == 403  # Forbidden

    @pytest.mark.asyncio
    async def test_get_user_profiles_success(self, live_client: AsyncClient):
        """Test successful retrieval of user profiles."""
        user_data = self._generate_unique_user_data("get_profiles")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create a profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201

        # Get profiles
        response = await live_client.get("/api/v1/profiles", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "profiles" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert len(data["profiles"]) == 1
        assert data["total"] == 1

        # Check profile data
        profile = data["profiles"][0]
        assert profile["personal_info"]["full_name"] == profile_data["personal_info"]["full_name"]

    @pytest.mark.asyncio
    async def test_get_user_profiles_pagination(self, live_client: AsyncClient):
        """Test user profiles pagination."""
        user_data = self._generate_unique_user_data("pagination")
        headers = await self._get_auth_headers(live_client, user_data)

        # Create multiple profiles (if supported) or just test pagination params
        response = await live_client.get("/api/v1/profiles?limit=5&offset=0", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 5
        assert data["offset"] == 0

    @pytest.mark.asyncio
    async def test_get_user_profiles_invalid_pagination(self, live_client: AsyncClient):
        """Test user profiles retrieval fails with invalid pagination."""
        user_data = self._generate_unique_user_data("invalid_pagination")
        headers = await self._get_auth_headers(live_client, user_data)

        # Test invalid limit
        response = await live_client.get("/api/v1/profiles?limit=0", headers=headers)
        assert response.status_code == 422

        # Test invalid offset
        response = await live_client.get("/api/v1/profiles?offset=-1", headers=headers)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_single_profile_success(self, live_client: AsyncClient):
        """Test successful retrieval of single profile."""
        user_data = self._generate_unique_user_data("get_single")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create a profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Get the specific profile
        response = await live_client.get(f"/api/v1/profiles/{profile_id}", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Check profile data
        assert data["id"] == profile_id
        assert data["personal_info"]["full_name"] == profile_data["personal_info"]["full_name"]
        assert data["professional_summary"] == profile_data["professional_summary"]

    @pytest.mark.asyncio
    async def test_get_single_profile_not_found(self, live_client: AsyncClient):
        """Test single profile retrieval fails when profile doesn't exist."""
        user_data = self._generate_unique_user_data("not_found")
        headers = await self._get_auth_headers(live_client, user_data)

        response = await live_client.get("/api/v1/profiles/nonexistent-id", headers=headers)
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_single_profile_wrong_owner(self, live_client: AsyncClient):
        """Test single profile retrieval fails when accessing another user's profile."""
        # Create first user and profile
        user1_data = self._generate_unique_user_data("user1")
        headers1 = await self._get_auth_headers(live_client, user1_data)
        profile_data = self._get_sample_profile_data()

        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers1)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Create second user
        user2_data = self._generate_unique_user_data("user2")
        headers2 = await self._get_auth_headers(live_client, user2_data)

        # Try to access first user's profile with second user's token
        response = await live_client.get(f"/api/v1/profiles/{profile_id}", headers=headers2)
        assert response.status_code == 403
        data = response.json()
        assert "access denied" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_profile_success(self, live_client: AsyncClient):
        """Test successful profile update."""
        user_data = self._generate_unique_user_data("update")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create a profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Update the profile
        update_data = {
            "professional_summary": "Updated professional summary with new achievements.",
            "personal_info": {
                **profile_data["personal_info"],
                "location": "San Francisco, CA"  # Changed location
            }
        }

        response = await live_client.put(f"/api/v1/profiles/{profile_id}", json=update_data, headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Check updated data
        assert data["professional_summary"] == update_data["professional_summary"]
        assert data["personal_info"]["location"] == "San Francisco, CA"

    @pytest.mark.asyncio
    async def test_update_profile_invalid_data(self, live_client: AsyncClient):
        """Test profile update fails with invalid data."""
        user_data = self._generate_unique_user_data("update_invalid")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create a profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Try to update with invalid data
        invalid_update = {
            "personal_info": {
                "full_name": "",  # Invalid
                "email": "not-an-email"  # Invalid
            }
        }

        response = await live_client.put(f"/api/v1/profiles/{profile_id}", json=invalid_update, headers=headers)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_delete_profile_success(self, live_client: AsyncClient):
        """Test successful profile deletion."""
        user_data = self._generate_unique_user_data("delete")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create a profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Delete the profile
        response = await live_client.delete(f"/api/v1/profiles/{profile_id}", headers=headers)
        assert response.status_code == 204  # No content

        # Verify profile is gone
        get_response = await live_client.get(f"/api/v1/profiles/{profile_id}", headers=headers)
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_profile_not_found(self, live_client: AsyncClient):
        """Test profile deletion fails when profile doesn't exist."""
        user_data = self._generate_unique_user_data("delete_not_found")
        headers = await self._get_auth_headers(live_client, user_data)

        response = await live_client.delete("/api/v1/profiles/nonexistent-id", headers=headers)
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_profile_analytics_success(self, live_client: AsyncClient):
        """Test successful retrieval of profile analytics."""
        user_data = self._generate_unique_user_data("analytics")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Add some experience and education for better analytics
        profile_data["experiences"] = [
            {
                "id": "exp_1",
                "title": "Senior Developer",
                "company": "Tech Corp",
                "location": "Seattle, WA",
                "start_date": "2020-01-01",
                "end_date": "2023-01-01",
                "is_current": False,
                "description": "Led development of web applications",
                "achievements": ["Built scalable systems"]
            }
        ]
        profile_data["education"] = [
            {
                "id": "edu_1",
                "institution": "University of Washington",
                "degree": "BS",
                "field_of_study": "Computer Science",
                "start_date": "2016-01-01",
                "end_date": "2020-01-01",
                "gpa": 3.8,
                "honors": ["Summa Cum Laude"]
            }
        ]

        # Create a profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Get analytics
        response = await live_client.get(f"/api/v1/profiles/{profile_id}/analytics", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Check analytics structure
        assert "completeness" in data
        assert "statistics" in data
        assert "recommendations" in data

        # Check completeness scores
        completeness = data["completeness"]
        assert "overall" in completeness
        assert "personal_info" in completeness
        assert "professional_summary" in completeness
        assert "experiences" in completeness
        assert "education" in completeness
        assert "skills" in completeness
        assert "projects" in completeness

        # Check statistics
        statistics = data["statistics"]
        assert "total_experiences" in statistics
        assert "total_education" in statistics
        assert "total_skills" in statistics
        assert "total_projects" in statistics
        assert "years_of_experience" in statistics

        # Check recommendations
        assert isinstance(data["recommendations"], list)

    @pytest.mark.asyncio
    async def test_get_my_profile_success(self, live_client: AsyncClient):
        """Test successful retrieval of current user's active profile."""
        user_data = self._generate_unique_user_data("my_profile")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create a profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201

        # Check that get_user_profiles finds the profile
        profiles_response = await live_client.get("/api/v1/profiles", headers=headers)
        assert profiles_response.status_code == 200
        profiles_data = profiles_response.json()
        assert len(profiles_data["profiles"]) == 1

        # Get my profile
        response = await live_client.get("/api/v1/profiles/me", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Check profile data
        assert data["personal_info"]["full_name"] == profile_data["personal_info"]["full_name"]
        assert data["professional_summary"] == profile_data["professional_summary"]
        assert len(data["skills"]["technical"]) == len(profile_data["skills"]["technical"])

    @pytest.mark.asyncio
    async def test_get_my_profile_not_found(self, live_client: AsyncClient):
        """Test my profile retrieval fails when user has no profile."""
        user_data = self._generate_unique_user_data("no_profile")
        headers = await self._get_auth_headers(live_client, user_data)

        # Try to get profile without creating one
        response = await live_client.get("/api/v1/profiles/me", headers=headers)

        assert response.status_code == 404
        data = response.json()
        assert "no profile found" in data["detail"].lower()