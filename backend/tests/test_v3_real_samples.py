"""Integration test for V3 Sample Upload API with real files."""

import pytest
from httpx import AsyncClient
from pathlib import Path

from app.main import app
from app.core.dependencies import get_current_user


# Mock user dependency
async def override_get_current_user():
    """Override for authenticated user - returns user_id as int."""
    return 1


@pytest.mark.asyncio
async def test_upload_huy_resume():
    """Test uploading Huy Ky's actual resume."""
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    # Read real resume file
    resume_path = Path(__file__).parent.parent.parent / "docs" / "sample artifacts" / "Huy_Ky_Enhanced_Resume.txt"
    resume_content = resume_path.read_text(encoding='utf-8')
    
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "resume"},
            files={"file": ("Huy_Ky_Enhanced_Resume.txt", resume_content, "text/plain")}
        )
    
    app.dependency_overrides.clear()
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify response structure
    assert data["document_type"] == "resume"
    assert data["original_filename"] == "Huy_Ky_Enhanced_Resume.txt"
    assert data["user_id"] == 1
    assert data["is_active"] is True
    
    # Verify metrics
    assert data["word_count"] == 1087  # Actual word count from file
    assert data["character_count"] == 8927  # Actual character count
    
    # Verify UUID format
    assert "id" in data
    assert len(data["id"]) == 36  # UUID format
    
    print(f"✅ Resume uploaded: {data['word_count']} words, {data['character_count']} chars")


@pytest.mark.asyncio
async def test_upload_huy_cover_letter():
    """Test uploading Huy Ky's actual cover letter."""
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    # Read real cover letter file
    cover_letter_path = Path(__file__).parent.parent.parent / "docs" / "sample artifacts" / "Huy_Ky_General_Cover_Letter.txt"
    cover_letter_content = cover_letter_path.read_text(encoding='utf-8')
    
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "cover_letter"},
            files={"file": ("Huy_Ky_General_Cover_Letter.txt", cover_letter_content, "text/plain")}
        )
    
    app.dependency_overrides.clear()
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify response structure
    assert data["document_type"] == "cover_letter"
    assert data["original_filename"] == "Huy_Ky_General_Cover_Letter.txt"
    assert data["user_id"] == 1
    assert data["is_active"] is True
    
    # Verify metrics
    assert data["word_count"] == 346  # Actual word count from file
    assert data["character_count"] == 2506  # Actual character count
    
    print(f"✅ Cover letter uploaded: {data['word_count']} words, {data['character_count']} chars")


@pytest.mark.asyncio
async def test_upload_both_samples_and_list():
    """Test uploading both samples and retrieving the list."""
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    # Read files
    resume_path = Path(__file__).parent.parent.parent / "docs" / "sample artifacts" / "Huy_Ky_Enhanced_Resume.txt"
    cover_letter_path = Path(__file__).parent.parent.parent / "docs" / "sample artifacts" / "Huy_Ky_General_Cover_Letter.txt"
    
    resume_content = resume_path.read_text(encoding='utf-8')
    cover_letter_content = cover_letter_path.read_text(encoding='utf-8')
    
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Upload resume
        resume_response = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "resume"},
            files={"file": ("Huy_Ky_Enhanced_Resume.txt", resume_content, "text/plain")}
        )
        assert resume_response.status_code == 201
        resume_data = resume_response.json()
        assert resume_data["word_count"] == 1087
        assert resume_data["character_count"] == 8927
        
        # Upload cover letter
        cover_response = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "cover_letter"},
            files={"file": ("Huy_Ky_General_Cover_Letter.txt", cover_letter_content, "text/plain")}
        )
        assert cover_response.status_code == 201
        cover_data = cover_response.json()
        assert cover_data["word_count"] == 346
        assert cover_data["character_count"] == 2506
        
        # Get list of samples
        list_response = await client.get("/api/v1/samples")
        assert list_response.status_code == 200
        
        list_data = list_response.json()
        assert list_data["total"] >= 2
        
        # Verify both samples are in the list
        sample_types = [s["document_type"] for s in list_data["samples"]]
        assert "resume" in sample_types
        assert "cover_letter" in sample_types
        
        # Verify no full text in list (performance optimization)
        for sample in list_data["samples"]:
            assert "original_text" not in sample
    
    print("✅ Both samples uploaded and listed correctly")
    print(f"   Resume: {resume_data['word_count']} words, {resume_data['character_count']} chars")
    print(f"   Cover Letter: {cover_data['word_count']} words, {cover_data['character_count']} chars")
    
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_sample_replacement():
    """Test that uploading new sample deactivates previous one."""
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    resume_path = Path(__file__).parent.parent.parent / "docs" / "sample artifacts" / "Huy_Ky_Enhanced_Resume.txt"
    resume_content = resume_path.read_text(encoding='utf-8')
    
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Upload first resume
        response1 = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "resume"},
            files={"file": ("resume_v1.txt", resume_content, "text/plain")}
        )
        assert response1.status_code == 201
        id1 = response1.json()["id"]
        
        # Upload second resume (should deactivate first)
        response2 = await client.post(
            "/api/v1/samples/upload",
            data={"document_type": "resume"},
            files={"file": ("resume_v2.txt", resume_content, "text/plain")}
        )
        assert response2.status_code == 201
        id2 = response2.json()["id"]
        
        # Get all samples including inactive
        all_samples = await client.get("/api/v1/samples?active_only=false")
        assert all_samples.status_code == 200
        
        samples = all_samples.json()["samples"]
        resume_samples = [s for s in samples if s["id"] in [id1, id2]]
        
        # Verify only the latest is active
        assert len(resume_samples) == 2
        active_count = sum(1 for s in resume_samples if s["is_active"])
        assert active_count == 1
        
        # Verify the second upload is the active one
        active_sample = next(s for s in resume_samples if s["is_active"])
        assert active_sample["id"] == id2
        assert active_sample["original_filename"] == "resume_v2.txt"
        
        print(f"✅ Sample replacement works correctly")
    
    app.dependency_overrides.clear()
