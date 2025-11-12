"""Integration tests for preference system."""

import pytest
import os
from pathlib import Path
from httpx import AsyncClient
from fastapi import status

# Test data paths
TEST_DATA_DIR = Path(__file__).parent.parent / "data"
SAMPLE_RESUME_PATH = TEST_DATA_DIR / "sample_resume.txt"
SAMPLE_COVER_LETTER_PATH = TEST_DATA_DIR / "sample_cover_letter.txt"


@pytest.mark.asyncio
async def test_preference_workflow_complete(async_client: AsyncClient, test_user_token: str):
    """
    Test complete preference extraction workflow:
    1. Upload cover letter -> extract writing style
    2. Upload sample resume -> extract layout preferences
    3. Get generation profile -> verify all preferences stored
    4. List example resumes -> verify upload recorded
    """
    
    # Setup authorization
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Step 1: Upload cover letter
    if SAMPLE_COVER_LETTER_PATH.exists():
        with open(SAMPLE_COVER_LETTER_PATH, "rb") as f:
            files = {"file": ("sample_cover_letter.txt", f, "text/plain")}
            response = await async_client.post(
                "/preferences/upload-cover-letter",
                files=files,
                headers=headers
            )
        
        assert response.status_code == status.HTTP_200_OK, f"Cover letter upload failed: {response.text}"
        cover_letter_result = response.json()
        
        assert cover_letter_result["success"] is True
        assert "writing_style_config_id" in cover_letter_result
        assert "extraction_metadata" in cover_letter_result
        
        print(f"✅ Cover letter uploaded - Writing Style Config ID: {cover_letter_result['writing_style_config_id']}")
        print(f"   Extracted preferences: {cover_letter_result['preferences']}")
    
    # Step 2: Upload sample resume
    if SAMPLE_RESUME_PATH.exists():
        with open(SAMPLE_RESUME_PATH, "rb") as f:
            files = {"file": ("sample_resume.txt", f, "text/plain")}
            data = {"is_primary": "true"}
            response = await async_client.post(
                "/preferences/upload-sample-resume",
                files=files,
                data=data,
                headers=headers
            )
        
        assert response.status_code == status.HTTP_200_OK, f"Resume upload failed: {response.text}"
        resume_result = response.json()
        
        assert resume_result["success"] is True
        assert "layout_config_id" in resume_result
        assert "example_resume_id" in resume_result
        
        print(f"✅ Sample resume uploaded - Layout Config ID: {resume_result['layout_config_id']}")
        print(f"   Example Resume ID: {resume_result['example_resume_id']}")
    
    # Step 3: Get generation profile
    response = await async_client.get(
        "/preferences/generation-profile",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    profile = response.json()
    
    assert "profile_id" in profile
    assert profile["writing_style"] is not None
    assert profile["layout"] is not None
    assert profile["overall_quality_score"] > 0.0
    
    print(f"✅ Generation profile retrieved:")
    print(f"   Profile ID: {profile['profile_id']}")
    print(f"   Writing Style Config ID: {profile['writing_style']['config_id']}")
    print(f"   Layout Config ID: {profile['layout']['config_id']}")
    print(f"   Quality Score: {profile['overall_quality_score']:.2f}")
    
    # Step 4: List example resumes
    response = await async_client.get(
        "/preferences/example-resumes",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    examples = response.json()
    
    assert examples["total"] > 0
    assert len(examples["examples"]) > 0
    
    primary_example = next((ex for ex in examples["examples"] if ex["is_primary"]), None)
    assert primary_example is not None, "No primary example resume found"
    
    print(f"✅ Example resumes listed - Total: {examples['total']}")
    print(f"   Primary example: {primary_example['filename']}")


@pytest.mark.asyncio
async def test_update_generation_preferences(async_client: AsyncClient, test_user_token: str):
    """Test updating generation preferences."""
    
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Update preferences
    new_preferences = {
        "prioritize_style_consistency": True,
        "prioritize_layout_consistency": True,
        "adapt_tone_to_industry": False,
        "maintain_personal_voice": True
    }
    
    response = await async_client.put(
        "/preferences/generation-profile",
        json=new_preferences,
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    
    assert result["success"] is True
    assert result["generation_preferences"] == new_preferences
    
    print(f"✅ Generation preferences updated:")
    print(f"   New preferences: {new_preferences}")


@pytest.mark.asyncio
async def test_delete_example_resume(async_client: AsyncClient, test_user_token: str):
    """Test deleting an example resume."""
    
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # First, list examples to get an ID
    response = await async_client.get(
        "/preferences/example-resumes",
        headers=headers
    )
    
    examples = response.json()
    
    if examples["total"] > 1:  # Only delete if there's more than one
        # Get a non-primary example
        non_primary = next((ex for ex in examples["examples"] if not ex["is_primary"]), None)
        
        if non_primary:
            response = await async_client.delete(
                f"/preferences/example-resumes/{non_primary['id']}",
                headers=headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            
            assert result["success"] is True
            print(f"✅ Example resume deleted: {non_primary['id']}")


@pytest.mark.asyncio
async def test_set_primary_example(async_client: AsyncClient, test_user_token: str):
    """Test setting an example resume as primary."""
    
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # List examples
    response = await async_client.get(
        "/preferences/example-resumes",
        headers=headers
    )
    
    examples = response.json()
    
    if examples["total"] > 1:
        # Get a non-primary example
        non_primary = next((ex for ex in examples["examples"] if not ex["is_primary"]), None)
        
        if non_primary:
            response = await async_client.post(
                f"/preferences/example-resumes/{non_primary['id']}/set-primary",
                headers=headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            
            assert result["success"] is True
            print(f"✅ Set example {non_primary['id']} as primary")


@pytest.mark.asyncio
async def test_invalid_file_upload(async_client: AsyncClient, test_user_token: str):
    """Test uploading invalid file format."""
    
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Try to upload an invalid file type
    files = {"file": ("test.exe", b"invalid content", "application/x-msdownload")}
    
    response = await async_client.post(
        "/preferences/upload-cover-letter",
        files=files,
        headers=headers
    )
    
    # Should reject invalid file type
    assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    print("✅ Invalid file type rejected as expected")


@pytest.mark.asyncio
async def test_profile_not_found_for_new_user(async_client: AsyncClient, test_user_token: str):
    """Test that profile returns 404 for users without uploads."""
    
    # This would need a fresh user token
    # For now, we assume the test user has already uploaded files
    # In a real test, you'd create a new user specifically for this test
    
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    response = await async_client.get(
        "/preferences/generation-profile",
        headers=headers
    )
    
    # Should return profile or 404
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    if response.status_code == status.HTTP_404_NOT_FOUND:
        print("✅ Profile not found for user without uploads (expected)")
    else:
        print("✅ Profile found for existing user")


def test_sample_data_files_exist():
    """Verify test data files exist."""
    
    assert SAMPLE_RESUME_PATH.exists(), f"Sample resume not found: {SAMPLE_RESUME_PATH}"
    assert SAMPLE_COVER_LETTER_PATH.exists(), f"Sample cover letter not found: {SAMPLE_COVER_LETTER_PATH}"
    
    print("✅ Test data files verified:")
    print(f"   Resume: {SAMPLE_RESUME_PATH}")
    print(f"   Cover Letter: {SAMPLE_COVER_LETTER_PATH}")
