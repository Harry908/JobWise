"""Basic integration tests for Generation API."""

import pytest
from httpx import AsyncClient

from app.main import app
from app.core.dependencies import get_current_user


# Mock user dependency
async def override_get_current_user():
    """Override for authenticated user."""
    return 1  # Return user_id


@pytest.fixture
def authenticated_client():
    """Create authenticated test client."""
    app.dependency_overrides[get_current_user] = override_get_current_user
    client = AsyncClient(app=app, base_url="http://testserver/api/v1")
    yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_templates(authenticated_client):
    """Test listing available templates (no dependencies needed)."""
    async with authenticated_client as client:
        response = await client.get("/generations/templates")

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
async def test_list_generations_empty(authenticated_client):
    """Test listing generations when none exist."""
    async with authenticated_client as client:
        response = await client.get("/generations")

        assert response.status_code == 200
        data = response.json()
        assert "generations" in data
        assert "pagination" in data
        assert "statistics" in data
        assert isinstance(data["generations"], list)
