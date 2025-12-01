"""Live tests for Sample Upload API using real test files."""

import pytest
import requests
import os
from pathlib import Path


# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Test user credentials (test user should already exist)
TEST_USER = {
    "email": "test@example.com",
    "password": "TestPass123"
}

# Test file paths (from workspace root)
TEST_RESUME_FILE = Path(__file__).parent.parent.parent / "Huy_Ky_Enhanced_Resume.txt"
TEST_COVER_LETTER_FILE = Path(__file__).parent.parent.parent / "Huy_Ky_General_Cover_Letter.txt"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for test user."""
    # Login to get token
    response = requests.post(
        f"{API_V1}/auth/login",
        json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    return data["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Get headers with authentication token."""
    return {"Authorization": f"Bearer {auth_token}"}


class TestSampleUploadAPI:
    """Test suite for Sample Upload API."""

    def test_01_upload_resume_sample(self, auth_headers):
        """Test uploading a resume sample."""
        # Verify test file exists
        assert TEST_RESUME_FILE.exists(), f"Resume file not found: {TEST_RESUME_FILE}"
        
        with open(TEST_RESUME_FILE, 'rb') as f:
            files = {'file': ('Huy_Ky_Enhanced_Resume.txt', f, 'text/plain')}
            data = {'document_type': 'resume'}
            
            response = requests.post(
                f"{API_V1}/samples/upload",
                headers=auth_headers,
                files=files,
                data=data
            )
        
        print(f"\n[TEST] Upload Resume - Status: {response.status_code}")
        print(f"Response: {response.json() if response.status_code in [200, 201] else response.text}")
        
        assert response.status_code == 201, f"Upload failed: {response.text}"
        
        data = response.json()
        assert data["document_type"] == "resume"
        assert data["original_filename"] == "Huy_Ky_Enhanced_Resume.txt"
        assert data["is_active"] == True
        assert data["word_count"] > 0
        assert data["character_count"] > 0
        assert "id" in data
        
        # Store sample ID for later tests
        pytest.resume_sample_id = data["id"]

    def test_02_upload_cover_letter_sample(self, auth_headers):
        """Test uploading a cover letter sample."""
        # Verify test file exists
        assert TEST_COVER_LETTER_FILE.exists(), f"Cover letter file not found: {TEST_COVER_LETTER_FILE}"
        
        with open(TEST_COVER_LETTER_FILE, 'rb') as f:
            files = {'file': ('Huy_Ky_General_Cover_Letter.txt', f, 'text/plain')}
            data = {'document_type': 'cover_letter'}
            
            response = requests.post(
                f"{API_V1}/samples/upload",
                headers=auth_headers,
                files=files,
                data=data
            )
        
        print(f"\n[TEST] Upload Cover Letter - Status: {response.status_code}")
        print(f"Response: {response.json() if response.status_code in [200, 201] else response.text}")
        
        assert response.status_code == 201, f"Upload failed: {response.text}"
        
        data = response.json()
        assert data["document_type"] == "cover_letter"
        assert data["original_filename"] == "Huy_Ky_General_Cover_Letter.txt"
        assert data["is_active"] == True
        assert data["word_count"] > 0
        assert data["character_count"] > 0
        
        # Store sample ID for later tests
        pytest.cover_letter_sample_id = data["id"]

    def test_03_list_all_samples(self, auth_headers):
        """Test listing all samples."""
        response = requests.get(
            f"{API_V1}/samples",
            headers=auth_headers
        )
        
        print(f"\n[TEST] List All Samples - Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "samples" in data
        assert "total" in data
        assert data["total"] >= 2  # At least resume and cover letter
        assert len(data["samples"]) == data["total"]

    def test_04_list_samples_filter_by_type(self, auth_headers):
        """Test listing samples filtered by document type."""
        # Filter by resume
        response = requests.get(
            f"{API_V1}/samples?document_type=resume",
            headers=auth_headers
        )
        
        print(f"\n[TEST] List Resumes - Status: {response.status_code}")
        
        assert response.status_code == 200
        data = response.json()
        assert all(s["document_type"] == "resume" for s in data["samples"])
        
        # Filter by cover_letter
        response = requests.get(
            f"{API_V1}/samples?document_type=cover_letter",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(s["document_type"] == "cover_letter" for s in data["samples"])

    def test_05_list_samples_filter_by_active(self, auth_headers):
        """Test listing samples filtered by active status."""
        response = requests.get(
            f"{API_V1}/samples?is_active=true",
            headers=auth_headers
        )
        
        print(f"\n[TEST] List Active Samples - Status: {response.status_code}")
        
        assert response.status_code == 200
        data = response.json()
        assert all(s["is_active"] == True for s in data["samples"])

    def test_06_get_sample_details(self, auth_headers):
        """Test getting sample details with full text."""
        response = requests.get(
            f"{API_V1}/samples/{pytest.resume_sample_id}",
            headers=auth_headers
        )
        
        print(f"\n[TEST] Get Sample Details - Status: {response.status_code}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == pytest.resume_sample_id
        assert "full_text" in data
        assert len(data["full_text"]) > 0
        assert data["word_count"] > 0
        assert data["character_count"] > 0
        
        # Verify word and character counts are accurate
        word_count = len(data["full_text"].split())
        assert data["word_count"] == word_count
        assert data["character_count"] == len(data["full_text"])

    def test_07_active_sample_toggling(self, auth_headers):
        """Test that uploading a new sample deactivates the previous one."""
        # Upload another resume sample
        with open(TEST_RESUME_FILE, 'rb') as f:
            files = {'file': ('Updated_Resume.txt', f, 'text/plain')}
            data = {'document_type': 'resume'}
            
            response = requests.post(
                f"{API_V1}/samples/upload",
                headers=auth_headers,
                files=files,
                data=data
            )
        
        print(f"\n[TEST] Upload Second Resume - Status: {response.status_code}")
        
        assert response.status_code == 201
        new_sample = response.json()
        assert new_sample["is_active"] == True
        
        # Check that the old resume is now inactive
        response = requests.get(
            f"{API_V1}/samples/{pytest.resume_sample_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        old_sample = response.json()
        assert old_sample["is_active"] == False
        
        # Store new sample ID
        pytest.new_resume_sample_id = new_sample["id"]

    def test_08_invalid_file_type(self, auth_headers):
        """Test that non-.txt files are rejected."""
        # Create a temporary .pdf file (just for testing validation)
        temp_file = Path(__file__).parent.parent / "temp_test.pdf"
        temp_file.write_text("This is not a valid PDF, just for testing")
        
        try:
            with open(temp_file, 'rb') as f:
                files = {'file': ('test.pdf', f, 'application/pdf')}
                data = {'document_type': 'resume'}
                
                response = requests.post(
                    f"{API_V1}/samples/upload",
                    headers=auth_headers,
                    files=files,
                    data=data
                )
            
            print(f"\n[TEST] Invalid File Type - Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            assert response.status_code == 400
            assert "Only .txt files are supported" in response.json()["detail"]
        finally:
            temp_file.unlink()  # Clean up

    def test_09_invalid_document_type(self, auth_headers):
        """Test that invalid document types are rejected."""
        with open(TEST_RESUME_FILE, 'rb') as f:
            files = {'file': ('resume.txt', f, 'text/plain')}
            data = {'document_type': 'invalid_type'}
            
            response = requests.post(
                f"{API_V1}/samples/upload",
                headers=auth_headers,
                files=files,
                data=data
            )
        
        print(f"\n[TEST] Invalid Document Type - Status: {response.status_code}")
        
        assert response.status_code == 400
        assert "must be 'resume' or 'cover_letter'" in response.json()["detail"]

    def test_10_empty_file_rejection(self, auth_headers):
        """Test that empty files are rejected."""
        # Create a temporary empty file
        temp_file = Path(__file__).parent.parent / "temp_empty.txt"
        temp_file.write_text("")
        
        try:
            with open(temp_file, 'rb') as f:
                files = {'file': ('empty.txt', f, 'text/plain')}
                data = {'document_type': 'resume'}
                
                response = requests.post(
                    f"{API_V1}/samples/upload",
                    headers=auth_headers,
                    files=files,
                    data=data
                )
            
            print(f"\n[TEST] Empty File - Status: {response.status_code}")
            
            assert response.status_code == 422
            assert "empty" in response.json()["detail"].lower()
        finally:
            temp_file.unlink()  # Clean up

    def test_11_delete_sample(self, auth_headers):
        """Test deleting a sample."""
        response = requests.delete(
            f"{API_V1}/samples/{pytest.new_resume_sample_id}",
            headers=auth_headers
        )
        
        print(f"\n[TEST] Delete Sample - Status: {response.status_code}")
        
        assert response.status_code == 204
        
        # Verify sample is deleted
        response = requests.get(
            f"{API_V1}/samples/{pytest.new_resume_sample_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_12_delete_nonexistent_sample(self, auth_headers):
        """Test deleting a non-existent sample."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.delete(
            f"{API_V1}/samples/{fake_id}",
            headers=auth_headers
        )
        
        print(f"\n[TEST] Delete Nonexistent - Status: {response.status_code}")
        
        assert response.status_code == 404

    def test_13_unauthorized_access(self):
        """Test that endpoints require authentication."""
        # Try to list samples without token
        response = requests.get(f"{API_V1}/samples")
        
        print(f"\n[TEST] Unauthorized Access - Status: {response.status_code}")
        
        # Accept either 401 or 403 as both indicate authentication required
        assert response.status_code in [401, 403]


if __name__ == "__main__":
    print("="*70)
    print("Sample Upload API - Live Tests")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_USER['email']}")
    print(f"Resume File: {TEST_RESUME_FILE}")
    print(f"Cover Letter File: {TEST_COVER_LETTER_FILE}")
    print("="*70 + "\n")
    
    pytest.main([__file__, "-v", "-s"])
