"""Tests for Generation API."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from datetime import datetime, timedelta

from app.main import app
from app.core.dependencies import get_current_user


# Mock user dependency
async def override_get_current_user():
    """Override for authenticated user."""
    return 1  # Return user_id


class TestGenerationAPI:
    """Test Generation API endpoints."""

    @pytest.mark.asyncio
    async def test_start_resume_generation_success(self, authenticated_client, test_profile, test_job):
        """Test successful resume generation start."""
        async with authenticated_client as client:
            response = await client.post(
                "/generations/resume",
                json={
                    "profile_id": test_profile["id"],
                    "job_id": test_job["id"],
                    "options": {
                        "template": "modern",
                        "length": "one_page",
                        "focus_areas": ["backend_development", "leadership"]
                    }
                }
            )

            assert response.status_code == 201
            data = response.json()
            assert "id" in data  # CRITICAL: Must be 'id' not 'generation_id'
            assert data["status"] == "pending"
            assert data["progress"]["current_stage"] == 0
            assert data["progress"]["percentage"] == 0
            assert data["profile_id"] == test_profile["id"]
            assert data["job_id"] == test_job["id"]
            assert "Location" in response.headers

    @pytest.mark.asyncio
    async def test_start_cover_letter_generation_success(self, client: AsyncClient, auth_headers, test_profile, test_job):
        """Test successful cover letter generation start."""
        response = await client.post(
            "/api/v1/generations/cover-letter",
            headers=auth_headers,
            json={
                "profile_id": test_profile["id"],
                "job_id": test_job["id"]
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["document_type"] == "cover_letter"

    @pytest.mark.asyncio
    async def test_get_generation_status(self, client: AsyncClient, auth_headers, test_generation):
        """Test getting generation status."""
        response = await client.get(
            f"/api/v1/generations/{test_generation['id']}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_generation["id"]
        assert "progress" in data
        assert "percentage" in data["progress"]

    @pytest.mark.asyncio
    async def test_progress_calculation(self, client: AsyncClient, auth_headers, test_profile, test_job):
        """Test progress percentage calculation with stage weights."""
        # Start generation
        response = await client.post(
            "/api/v1/generations/resume",
            headers=auth_headers,
            json={
                "profile_id": test_profile["id"],
                "job_id": test_job["id"]
            }
        )
        generation_id = response.json()["id"]

        # Wait a bit for pipeline to progress
        import asyncio
        await asyncio.sleep(0.5)

        # Check status
        response = await client.get(
            f"/api/v1/generations/{generation_id}",
            headers=auth_headers
        )

        data = response.json()
        progress = data["progress"]

        # Verify stage weights: [20, 20, 40, 15, 5]
        stage_to_percentage = {
            0: 0,
            1: 20,
            2: 40,
            3: 80,
            4: 95,
            5: 100
        }

        current_stage = progress["current_stage"]
        expected_percentage = stage_to_percentage.get(current_stage, 0)
        assert progress["percentage"] == expected_percentage

    @pytest.mark.asyncio
    async def test_get_generation_result_completed(self, client: AsyncClient, auth_headers, test_completed_generation):
        """Test getting final result for completed generation."""
        response = await client.get(
            f"/api/v1/generations/{test_completed_generation['id']}/result",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert "ats_score" in data
        assert "match_percentage" in data
        assert "keyword_coverage" in data
        assert "recommendations" in data

    @pytest.mark.asyncio
    async def test_get_generation_result_not_completed(self, client: AsyncClient, auth_headers, test_generation):
        """Test getting result for non-completed generation fails."""
        response = await client.get(
            f"/api/v1/generations/{test_generation['id']}/result",
            headers=auth_headers
        )

        assert response.status_code == 400  # Not completed

    @pytest.mark.asyncio
    async def test_list_generations(self, client: AsyncClient, auth_headers):
        """Test listing generations."""
        response = await client.get(
            "/api/v1/generations",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "generations" in data
        assert "pagination" in data
        assert "statistics" in data
        assert isinstance(data["generations"], list)

    @pytest.mark.asyncio
    async def test_list_generations_with_filters(self, client: AsyncClient, auth_headers, test_job):
        """Test listing generations with filters."""
        response = await client.get(
            "/api/v1/generations",
            headers=auth_headers,
            params={
                "job_id": test_job["id"],
                "status": "completed",
                "limit": 10
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["limit"] == 10

    @pytest.mark.asyncio
    async def test_regenerate(self, client: AsyncClient, auth_headers, test_completed_generation):
        """Test regenerating with new options."""
        response = await client.post(
            f"/api/v1/generations/{test_completed_generation['id']}/regenerate",
            headers=auth_headers,
            json={
                "options": {
                    "template": "creative",
                    "custom_instructions": "Focus on leadership"
                }
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] != test_completed_generation["id"]  # New generation
        assert "Location" in response.headers

    @pytest.mark.asyncio
    async def test_cancel_generation(self, client: AsyncClient, auth_headers, test_generation):
        """Test cancelling in-progress generation."""
        response = await client.delete(
            f"/api/v1/generations/{test_generation['id']}",
            headers=auth_headers
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_completed_generation(self, client: AsyncClient, auth_headers, test_completed_generation):
        """Test deleting completed generation."""
        response = await client.delete(
            f"/api/v1/generations/{test_completed_generation['id']}",
            headers=auth_headers
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_list_templates(self, client: AsyncClient, auth_headers):
        """Test listing available templates."""
        response = await client.get(
            "/api/v1/generations/templates",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert len(data["templates"]) == 3  # modern, classic, creative

        # Verify template structure
        for template in data["templates"]:
            assert "id" in template
            assert "name" in template
            assert "ats_friendly" in template
            assert template["id"] in ["modern", "classic", "creative"]

    @pytest.mark.asyncio
    async def test_rate_limiting(self, client: AsyncClient, auth_headers, test_profile, test_job):
        """Test rate limiting (10 generations per hour)."""
        # Create 10 generations
        for i in range(10):
            await client.post(
                "/api/v1/generations/resume",
                headers=auth_headers,
                json={
                    "profile_id": test_profile["id"],
                    "job_id": test_job["id"]
                }
            )

        # 11th should fail with 429
        response = await client.post(
            "/api/v1/generations/resume",
            headers=auth_headers,
            json={
                "profile_id": test_profile["id"],
                "job_id": test_job["id"]
            }
        )

        assert response.status_code == 429
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "rate_limit_exceeded"
        assert "retry_after" in data["error"]["details"]

    @pytest.mark.asyncio
    async def test_generation_not_found(self, client: AsyncClient, auth_headers):
        """Test accessing non-existent generation."""
        response = await client.get(
            "/api/v1/generations/nonexistent-id",
            headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_forbidden_access(self, client: AsyncClient, auth_headers, other_user_generation):
        """Test accessing another user's generation."""
        response = await client.get(
            f"/api/v1/generations/{other_user_generation['id']}",
            headers=auth_headers
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_validation_invalid_profile_id(self, client: AsyncClient, auth_headers, test_job):
        """Test validation for invalid profile ID."""
        response = await client.post(
            "/api/v1/generations/resume",
            headers=auth_headers,
            json={
                "profile_id": "invalid-uuid",
                "job_id": test_job["id"]
            }
        )

        # Should return 400 or 404 depending on validation
        assert response.status_code in [400, 404]

    @pytest.mark.asyncio
    async def test_stage_names_exact_match(self, client: AsyncClient, auth_headers, test_profile, test_job):
        """Test that stage names match specification exactly."""
        response = await client.post(
            "/api/v1/generations/resume",
            headers=auth_headers,
            json={
                "profile_id": test_profile["id"],
                "job_id": test_job["id"]
            }
        )
        generation_id = response.json()["id"]

        # Wait for pipeline to progress
        import asyncio
        await asyncio.sleep(1.0)

        response = await client.get(
            f"/api/v1/generations/{generation_id}",
            headers=auth_headers
        )

        data = response.json()
        stage_name = data["progress"]["stage_name"]

        # Verify exact stage names from spec
        valid_stage_names = [
            None,  # Stage 0
            "Job Analysis",
            "Profile Compilation",
            "Content Generation",
            "Quality Validation",
            "Export Preparation"
        ]

        assert stage_name in valid_stage_names


# Fixtures
@pytest.fixture
def authenticated_client():
    """Create authenticated test client."""
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield AsyncClient(app=app, base_url="http://testserver/api/v1")
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_profile(authenticated_client):
    """Create a test profile."""
    async with authenticated_client as client:
        response = await client.post(
            "/profiles",
            json={
                "personal_info": {
                    "full_name": "Test User",
                    "email": "test@example.com"
                },
                "skills": {
                    "technical": ["Python", "FastAPI"],
                    "soft": ["Leadership"]
                }
            }
        )
        return response.json()


@pytest_asyncio.fixture
async def test_job(authenticated_client):
    """Create a test job."""
    async with authenticated_client as client:
        response = await client.post(
            "/jobs",
            json={
                "raw_text": "Senior Python Developer at Test Corp\nLooking for a senior Python developer"
            }
        )
        return response.json()


@pytest_asyncio.fixture
async def test_generation(authenticated_client, test_profile, test_job):
    """Create a test generation."""
    async with authenticated_client as client:
        response = await client.post(
            "/generations/resume",
            json={
                "profile_id": test_profile["id"],
                "job_id": test_job["id"]
            }
        )
        return response.json()


@pytest_asyncio.fixture
async def test_completed_generation(authenticated_client, test_generation):
    """Wait for generation to complete."""
    import asyncio
    generation_id = test_generation["id"]

    # Poll until completed (max 3 seconds)
    async with authenticated_client as client:
        for _ in range(30):
            response = await client.get(
                f"/generations/{generation_id}"
            )
            data = response.json()
            if data["status"] == "completed":
                return data
            await asyncio.sleep(0.1)

    return test_generation  # Return anyway if not completed


@pytest.fixture
def other_user_generation():
    """Mock generation belonging to another user."""
    return {"id": "other-user-gen-id"}
