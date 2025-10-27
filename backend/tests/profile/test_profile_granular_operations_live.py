"""Live server tests for profile granular component operations and skills/custom fields."""

import time
import pytest
from httpx import AsyncClient


class TestProfileGranularOperationsLive:
    """Live server test suite for profile granular component operations."""

    @pytest.fixture
    def live_client(self):
        """Create HTTP client for live server testing."""
        return AsyncClient(base_url="http://localhost:8000", timeout=30.0)

    def _generate_unique_email(self, prefix: str = "test") -> str:
        """Generate unique email using timestamp to avoid duplicates."""
        timestamp = int(time.time() * 1000)
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
    async def test_get_skills_success(self, live_client: AsyncClient):
        """Test successful retrieval of skills."""
        user_data = self._generate_unique_user_data("get_skills")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Get skills
        response = await live_client.get(
            f"/api/v1/profiles/{profile_id}/skills",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "technical" in data
        assert "soft" in data
        assert "languages" in data
        assert "certifications" in data

        # Check skills data
        assert len(data["technical"]) == 4
        assert "Python" in data["technical"]
        assert "FastAPI" in data["technical"]

        assert len(data["soft"]) == 3
        assert "Leadership" in data["soft"]

        assert len(data["languages"]) == 2
        assert data["languages"][0]["name"] == "English"
        assert data["languages"][0]["proficiency"] == "native"

        assert len(data["certifications"]) == 1
        assert data["certifications"][0]["name"] == "AWS Solutions Architect"

    @pytest.mark.asyncio
    async def test_get_skills_unauthorized(self, live_client: AsyncClient):
        """Test skills retrieval fails without authentication."""
        response = await live_client.get("/api/v1/profiles/profile-123/skills")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_skills_wrong_owner(self, live_client: AsyncClient):
        """Test skills retrieval fails when accessing another user's profile."""
        # Create first user and profile
        user1_data = self._generate_unique_user_data("user1_skills")
        headers1 = await self._get_auth_headers(live_client, user1_data)
        profile_data = self._get_sample_profile_data()

        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers1)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Create second user
        user2_data = self._generate_unique_user_data("user2_skills")
        headers2 = await self._get_auth_headers(live_client, user2_data)

        # Try to access first user's skills
        response = await live_client.get(
            f"/api/v1/profiles/{profile_id}/skills",
            headers=headers2
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_add_technical_skills_success(self, live_client: AsyncClient):
        """Test successful addition of technical skills."""
        user_data = self._generate_unique_user_data("add_tech_skills")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Add technical skills
        new_skills = {
            "skills": ["Docker", "Kubernetes", "AWS", "Terraform", "Jenkins"]
        }

        response = await live_client.post(
            f"/api/v1/profiles/{profile_id}/skills/technical",
            json=new_skills,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check response
        assert "message" in data
        assert "skills added" in data["message"].lower()

        # Verify skills were added
        get_response = await live_client.get(
            f"/api/v1/profiles/{profile_id}/skills",
            headers=headers
        )
        assert get_response.status_code == 200
        skills_data = get_response.json()

        # Check that new skills are present
        assert "Docker" in skills_data["technical"]
        assert "Kubernetes" in skills_data["technical"]
        assert "AWS" in skills_data["technical"]

        # Check that original skills are still there
        assert "Python" in skills_data["technical"]
        assert "FastAPI" in skills_data["technical"]

    @pytest.mark.asyncio
    async def test_add_soft_skills_success(self, live_client: AsyncClient):
        """Test successful addition of soft skills."""
        user_data = self._generate_unique_user_data("add_soft_skills")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Add soft skills
        new_skills = {
            "skills": ["Project Management", "Team Leadership", "Problem Solving", "Public Speaking"]
        }

        response = await live_client.post(
            f"/api/v1/profiles/{profile_id}/skills/soft",
            json=new_skills,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check response
        assert "message" in data
        assert "skills added" in data["message"].lower()

        # Verify skills were added
        get_response = await live_client.get(
            f"/api/v1/profiles/{profile_id}/skills",
            headers=headers
        )
        assert get_response.status_code == 200
        skills_data = get_response.json()

        # Check that new skills are present
        assert "Project Management" in skills_data["soft"]
        assert "Team Leadership" in skills_data["soft"]

        # Check that original skills are still there
        assert "Leadership" in skills_data["soft"]
        assert "Communication" in skills_data["soft"]

    @pytest.mark.asyncio
    async def test_remove_technical_skills_success(self, live_client: AsyncClient):
        """Test successful removal of technical skills."""
        user_data = self._generate_unique_user_data("remove_tech_skills")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Remove some technical skills
        skills_to_remove = {
            "skills": ["React", "PostgreSQL"]
        }

        response = await live_client.request(
            "DELETE",
            f"/api/v1/profiles/{profile_id}/skills/technical",
            json=skills_to_remove,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check response
        assert "message" in data
        assert "skills removed" in data["message"].lower()

        # Verify skills were removed
        get_response = await live_client.get(
            f"/api/v1/profiles/{profile_id}/skills",
            headers=headers
        )
        assert get_response.status_code == 200
        skills_data = get_response.json()

        # Check that skills were removed
        assert "React" not in skills_data["technical"]
        assert "PostgreSQL" not in skills_data["technical"]

        # Check that other skills are still there
        assert "Python" in skills_data["technical"]
        assert "FastAPI" in skills_data["technical"]

    @pytest.mark.asyncio
    async def test_remove_soft_skills_success(self, live_client: AsyncClient):
        """Test successful removal of soft skills."""
        user_data = self._generate_unique_user_data("remove_soft_skills")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Remove some soft skills
        skills_to_remove = {
            "skills": ["Leadership", "Communication"]
        }

        response = await live_client.request(
            "DELETE",
            f"/api/v1/profiles/{profile_id}/skills/soft",
            json=skills_to_remove,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check response
        assert "message" in data
        assert "skills removed" in data["message"].lower()

        # Verify skills were removed
        get_response = await live_client.get(
            f"/api/v1/profiles/{profile_id}/skills",
            headers=headers
        )
        assert get_response.status_code == 200
        skills_data = get_response.json()

        # Check that skills were removed
        assert "Leadership" not in skills_data["soft"]
        assert "Communication" not in skills_data["soft"]

        # Check that other skills are still there
        assert "Problem Solving" in skills_data["soft"]

    @pytest.mark.asyncio
    async def test_update_skills_full_success(self, live_client: AsyncClient):
        """Test successful full update of all skills."""
        user_data = self._generate_unique_user_data("update_skills")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Update all skills
        updated_skills = {
            "technical": ["Python", "Go", "Rust", "Docker"],
            "soft": ["Leadership", "Mentoring"],
            "languages": [
                {"name": "English", "proficiency": "native"},
                {"name": "French", "proficiency": "fluent"},
                {"name": "Japanese", "proficiency": "basic"}
            ],
            "certifications": [
                {
                    "name": "Kubernetes Certified Administrator",
                    "issuer": "Cloud Native Computing Foundation",
                    "date_obtained": "2023-06-01",
                    "credential_id": "CKA-456"
                }
            ]
        }

        response = await live_client.put(
            f"/api/v1/profiles/{profile_id}/skills",
            json=updated_skills,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check response
        assert "message" in data
        assert "skills updated" in data["message"].lower()

        # Verify skills were updated
        get_response = await live_client.get(
            f"/api/v1/profiles/{profile_id}/skills",
            headers=headers
        )
        assert get_response.status_code == 200
        skills_data = get_response.json()

        # Check updated technical skills
        assert len(skills_data["technical"]) == 4
        assert "Go" in skills_data["technical"]
        assert "Rust" in skills_data["technical"]
        assert "React" not in skills_data["technical"]  # Should be replaced

        # Check updated soft skills
        assert len(skills_data["soft"]) == 2
        assert "Mentoring" in skills_data["soft"]
        assert "Communication" not in skills_data["soft"]  # Should be replaced

        # Check updated languages
        assert len(skills_data["languages"]) == 3
        assert skills_data["languages"][1]["name"] == "French"
        assert skills_data["languages"][1]["proficiency"] == "fluent"

        # Check updated certifications
        assert len(skills_data["certifications"]) == 1
        assert skills_data["certifications"][0]["name"] == "Kubernetes Certified Administrator"

    @pytest.mark.asyncio
    async def test_add_custom_fields_success(self, live_client: AsyncClient):
        """Test successful addition/update of custom fields."""
        user_data = self._generate_unique_user_data("add_custom")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Add custom fields
        custom_fields_data = {
            "fields": [
                {"key": "hobbies", "value": ["reading", "gaming", "photography"]},
                {"key": "achievements", "value": ["Employee of the Month", "Hackathon Winner"]},
                {"key": "interests", "value": ["AI/ML", "Open Source"]}
            ]
        }

        response = await live_client.post(
            f"/api/v1/profiles/{profile_id}/custom-fields",
            json=custom_fields_data,
            headers=headers
        )

        assert response.status_code == 201
        data = response.json()

        # Check response
        assert "message" in data
        assert "updated_fields" in data
        assert len(data["updated_fields"]) == 3
        assert "hobbies" in data["updated_fields"]
        assert "achievements" in data["updated_fields"]
        assert "interests" in data["updated_fields"]

        # Verify custom fields were added
        get_response = await live_client.get(
            f"/api/v1/profiles/{profile_id}/custom-fields",
            headers=headers
        )
        assert get_response.status_code == 200
        custom_data = get_response.json()

        # Check custom fields data
        assert "hobbies" in custom_data
        assert custom_data["hobbies"] == ["reading", "gaming", "photography"]

        assert "achievements" in custom_data
        assert custom_data["achievements"] == ["Employee of the Month", "Hackathon Winner"]

        assert "interests" in custom_data
        assert custom_data["interests"] == ["AI/ML", "Open Source"]

    @pytest.mark.asyncio
    async def test_get_custom_fields_success(self, live_client: AsyncClient):
        """Test successful retrieval of custom fields."""
        user_data = self._generate_unique_user_data("get_custom")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Add custom fields first
        custom_fields_data = {
            "fields": [
                {"key": "hobbies", "value": ["reading", "gaming"]},
                {"key": "achievements", "value": ["Employee of the Month"]}
            ]
        }

        await live_client.post(
            f"/api/v1/profiles/{profile_id}/custom-fields",
            json=custom_fields_data,
            headers=headers
        )

        # Get custom fields
        response = await live_client.get(
            f"/api/v1/profiles/{profile_id}/custom-fields",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check custom fields data
        assert "hobbies" in data
        assert data["hobbies"] == ["reading", "gaming"]

        assert "achievements" in data
        assert data["achievements"] == ["Employee of the Month"]

    @pytest.mark.asyncio
    async def test_update_custom_fields_success(self, live_client: AsyncClient):
        """Test successful update of custom fields."""
        user_data = self._generate_unique_user_data("update_custom")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Add initial custom fields
        initial_fields = {
            "fields": [
                {"key": "hobbies", "value": ["reading", "gaming"]},
                {"key": "achievements", "value": ["Employee of the Month"]}
            ]
        }

        await live_client.post(
            f"/api/v1/profiles/{profile_id}/custom-fields",
            json=initial_fields,
            headers=headers
        )

        # Update custom fields (full replacement)
        updated_fields = {
            "hobbies": ["reading", "gaming", "photography", "cooking"],
            "achievements": ["Employee of the Month", "Hackathon Winner", "Team Player Award"],
            "interests": ["AI/ML", "Open Source", "Sustainable Technology"],
            "volunteer_work": ["Code for America", "Local Hackathon Organizer"]
        }

        response = await live_client.put(
            f"/api/v1/profiles/{profile_id}/custom-fields",
            json=updated_fields,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check response contains all updated fields
        assert "hobbies" in data
        assert "achievements" in data
        assert "interests" in data
        assert "volunteer_work" in data

        # Check specific values
        assert len(data["hobbies"]) == 4
        assert "photography" in data["hobbies"]
        assert "cooking" in data["hobbies"]

        assert len(data["achievements"]) == 3
        assert "Team Player Award" in data["achievements"]

        assert data["interests"] == ["AI/ML", "Open Source", "Sustainable Technology"]
        assert data["volunteer_work"] == ["Code for America", "Local Hackathon Organizer"]

    @pytest.mark.asyncio
    async def test_custom_fields_operations_unauthorized(self, live_client: AsyncClient):
        """Test custom fields operations fail without authentication."""
        # Test POST
        response = await live_client.post(
            "/api/v1/profiles/profile-123/custom-fields",
            json={"fields": [{"key": "test", "value": "value"}]}
        )
        assert response.status_code == 403

        # Test GET
        response = await live_client.get("/api/v1/profiles/profile-123/custom-fields")
        assert response.status_code == 403

        # Test PUT
        response = await live_client.put(
            "/api/v1/profiles/profile-123/custom-fields",
            json={"test": "value"}
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_custom_fields_operations_wrong_owner(self, live_client: AsyncClient):
        """Test custom fields operations fail when accessing another user's profile."""
        # Create first user and profile
        user1_data = self._generate_unique_user_data("user1_custom")
        headers1 = await self._get_auth_headers(live_client, user1_data)
        profile_data = self._get_sample_profile_data()

        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers1)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Create second user
        user2_data = self._generate_unique_user_data("user2_custom")
        headers2 = await self._get_auth_headers(live_client, user2_data)

        # Try operations with second user
        response = await live_client.post(
            f"/api/v1/profiles/{profile_id}/custom-fields",
            json={"fields": [{"key": "test", "value": "value"}]},
            headers=headers2
        )
        assert response.status_code == 403

        response = await live_client.get(
            f"/api/v1/profiles/{profile_id}/custom-fields",
            headers=headers2
        )
        assert response.status_code == 403

        response = await live_client.put(
            f"/api/v1/profiles/{profile_id}/custom-fields",
            json={"test": "value"},
            headers=headers2
        )
        assert response.status_code == 403