"""Test suite for V3 Generation API - Sample Upload Endpoints."""

import pytest
import io
from httpx import AsyncClient
from unittest.mock import AsyncMock
from uuid import uuid4

from app.main import app
from app.core.dependencies import get_current_user, get_db_session


# Mock user dependency
async def override_get_current_user():
    """Override for authenticated user - returns user_id as int."""
    return 1


# Test fixtures
@pytest.fixture
def authenticated_client():
    """Client with authentication override."""
    app.dependency_overrides[get_current_user] = override_get_current_user
    client = AsyncClient(app=app, base_url="http://testserver")
    yield client
    app.dependency_overrides.clear()


# ==================== POST /samples/upload Tests ====================

@pytest.mark.asyncio
async def test_upload_resume_sample_success(authenticated_client):
    """Test successful resume sample upload."""
    # Create sample .txt file
    sample_content = "John Doe\nSenior Software Engineer\n\nEXPERIENCE\n" + "Python developer with 8 years experience.\n" * 20
    
    async with authenticated_client as client:
        response = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "resume"},
            files={"file": ("resume.txt", sample_content, "text/plain")}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["document_type"] == "resume"
    assert data["original_filename"] == "resume.txt"
    assert data["word_count"] > 0
    assert data["character_count"] > 0
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_upload_cover_letter_sample_success(authenticated_client):
    """Test successful cover letter sample upload."""
    sample_content = "Dear Hiring Manager,\n\nI am writing to express my interest...\n" * 10
    
    async with authenticated_client as client:
        response = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "cover_letter"},
            files={"file": ("cover_letter.txt", sample_content, "text/plain")}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["document_type"] == "cover_letter"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_upload_invalid_file_type(authenticated_client):
    """Test upload with non-.txt file returns 400."""
    sample_content = "Resume content"
    
    async with authenticated_client as client:
        response = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "resume"},
            files={"file": ("resume.pdf", sample_content, "application/pdf")}
        )
    
    assert response.status_code == 400
    assert "txt" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_invalid_document_type(authenticated_client):
    """Test upload with invalid document_type returns 400."""
    sample_content = "Resume content"
    
    async with authenticated_client as client:
        response = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "invalid_type"},
            files={"file": ("resume.txt", sample_content, "text/plain")}
        )
    
    assert response.status_code == 400
    assert "document_type" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_empty_file(authenticated_client):
    """Test upload with empty file returns 422."""
    async with authenticated_client as client:
        response = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "resume"},
            files={"file": ("resume.txt", "", "text/plain")}
        )
    
    assert response.status_code == 422
    assert "empty" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_file_too_large(authenticated_client):
    """Test upload with file exceeding 1MB returns 413."""
    # Create 2MB file
    large_content = "x" * (2 * 1024 * 1024)
    
    async with authenticated_client as client:
        response = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "resume"},
            files={"file": ("large.txt", large_content, "text/plain")}
        )
    
    assert response.status_code == 413
    assert "1mb" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_replaces_previous_sample(authenticated_client):
    """Test uploading new sample deactivates previous sample of same type."""
    sample1 = "First resume version"
    sample2 = "Second resume version"
    
    async with authenticated_client as client:
        # Upload first resume
        response1 = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "resume"},
            files={"file": ("resume1.txt", sample1, "text/plain")}
        )
        assert response1.status_code == 201
        
        # Upload second resume (should deactivate first)
        response2 = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "resume"},
            files={"file": ("resume2.txt", sample2, "text/plain")}
        )
        assert response2.status_code == 201
        
        # Get all samples
        samples_response = await client.get("/api/v1/samples?active_only=false")
        assert samples_response.status_code == 200
        
        # Should have 2 resume samples, only latest active
        samples = samples_response.json()["samples"]
        resume_samples = [s for s in samples if s["document_type"] == "resume"]
        
        if len(resume_samples) >= 2:
            active_count = sum(1 for s in resume_samples if s["is_active"])
            assert active_count == 1


@pytest.mark.asyncio
async def test_upload_unauthenticated(authenticated_client):
    """Test upload without authentication returns 401."""
    app.dependency_overrides.clear()
    
    sample_content = "Resume content"
    
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "resume"},
            files={"file": ("resume.txt", sample_content, "text/plain")}
        )
    
    assert response.status_code == 401


# ==================== GET /samples Tests ====================

@pytest.mark.asyncio
async def test_get_samples_list(authenticated_client):
    """Test getting list of uploaded samples."""
    async with authenticated_client as client:
        response = await client.get("/api/v1/samples")
    
    assert response.status_code == 200
    data = response.json()
    assert "samples" in data
    assert "total" in data
    assert isinstance(data["samples"], list)


@pytest.mark.asyncio
async def test_get_samples_filter_by_type(authenticated_client):
    """Test filtering samples by document type."""
    async with authenticated_client as client:
        response = await client.get("/api/v1/samples?document_type=resume")
    
    assert response.status_code == 200
    data = response.json()
    
    # All returned samples should be resumes
    for sample in data["samples"]:
        assert sample["document_type"] == "resume"


@pytest.mark.asyncio
async def test_get_samples_include_inactive(authenticated_client):
    """Test getting both active and inactive samples."""
    async with authenticated_client as client:
        response = await client.get("/api/v1/samples?active_only=false")
    
    assert response.status_code == 200
    data = response.json()
    assert "samples" in data


@pytest.mark.asyncio
async def test_get_samples_no_full_text(authenticated_client):
    """Test that list endpoint does not return full text."""
    async with authenticated_client as client:
        response = await client.get("/api/v1/samples")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should NOT have original_text field in list view
    for sample in data["samples"]:
        assert "original_text" not in sample
        assert "id" in sample
        assert "document_type" in sample


# ==================== GET /samples/{id} Tests ====================

@pytest.mark.asyncio
async def test_get_sample_detail_with_full_text(authenticated_client):
    """Test getting specific sample with full text."""
    # First upload a sample
    sample_content = "Detailed resume content for testing full text retrieval"
    
    async with authenticated_client as client:
        upload_response = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "resume"},
            files={"file": ("resume.txt", sample_content, "text/plain")}
        )
        assert upload_response.status_code == 201
        sample_id = upload_response.json()["id"]
        
        # Get sample detail
        detail_response = await client.get(f"/api/v1/samples/{sample_id}")
        
    assert detail_response.status_code == 200
    data = detail_response.json()
    assert "original_text" in data
    assert data["original_text"] == sample_content
    assert data["id"] == sample_id


@pytest.mark.asyncio
async def test_get_sample_not_found(authenticated_client):
    """Test getting non-existent sample returns 404."""
    fake_id = str(uuid4())
    
    async with authenticated_client as client:
        response = await client.get(f"/api/v1/samples/{fake_id}")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ==================== DELETE /samples/{id} Tests ====================

@pytest.mark.asyncio
async def test_delete_sample_success(authenticated_client):
    """Test successful sample deletion."""
    sample_content = "Sample to delete"
    
    async with authenticated_client as client:
        # Upload sample
        upload_response = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "resume"},
            files={"file": ("resume.txt", sample_content, "text/plain")}
        )
        assert upload_response.status_code == 201
        sample_id = upload_response.json()["id"]
        
        # Delete sample
        delete_response = await client.delete(f"/api/v1/samples/{sample_id}")
        
    assert delete_response.status_code == 204
    
    # Verify deletion - should return 404
    async with authenticated_client as client:
        get_response = await client.get(f"/api/v1/samples/{sample_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_sample_not_found(authenticated_client):
    """Test deleting non-existent sample returns 404."""
    fake_id = str(uuid4())
    
    async with authenticated_client as client:
        response = await client.delete(f"/api/v1/samples/{fake_id}")
    
    assert response.status_code == 404


# ==================== Validation Tests ====================

@pytest.mark.asyncio
async def test_upload_word_count_calculation(authenticated_client):
    """Test word count is calculated correctly."""
    sample_content = "one two three four five"  # 5 words
    
    async with authenticated_client as client:
        response = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "resume"},
            files={"file": ("resume.txt", sample_content, "text/plain")}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["word_count"] == 5


@pytest.mark.asyncio
async def test_upload_character_count_calculation(authenticated_client):
    """Test character count is calculated correctly."""
    sample_content = "Hello"  # 5 characters
    
    async with authenticated_client as client:
        response = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "resume"},
            files={"file": ("resume.txt", sample_content, "text/plain")}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["character_count"] == 5
