"""
Test script for job-specific exports endpoint
Tests the new GET /api/v1/exports/files/job/{job_id} endpoint
"""

import requests
import json


BASE_URL = "http://localhost:8000"
API_VERSION = "/api/v1"

# Test credentials - update with actual test user
TEST_EMAIL = "huyky@example.com"
TEST_PASSWORD = "password123"


def login() -> str:
    """Login and get access token."""
    response = requests.post(
        f"{BASE_URL}{API_VERSION}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Login successful: {data['user']['email']}")
        return data['access_token']
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None


def test_list_all_exports(token: str):
    """Test listing all exports."""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}{API_VERSION}/exports/files",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ List all exports successful")
        print(f"  Total exports: {data['total']}")
        print(f"  Exports returned: {len(data['exports'])}")
        
        # Print first export for inspection
        if data['exports']:
            first_export = data['exports'][0]
            print(f"\n  First export:")
            print(f"    ID: {first_export['id']}")
            print(f"    Job ID: {first_export.get('job_id', 'N/A')}")
            print(f"    Format: {first_export['format']}")
            print(f"    Filename: {first_export['filename']}")
            print(f"    Created: {first_export['created_at']}")
        
        return data['exports']
    else:
        print(f"❌ List all exports failed: {response.status_code}")
        print(response.text)
        return []


def test_list_exports_with_job_filter(token: str, job_id: str):
    """Test listing exports filtered by job_id."""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}{API_VERSION}/exports/files?job_id={job_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ List exports with job filter successful")
        print(f"  Job ID: {job_id}")
        print(f"  Total exports: {data['total']}")
        print(f"  Exports returned: {len(data['exports'])}")
        return data['exports']
    else:
        print(f"❌ List exports with job filter failed: {response.status_code}")
        print(response.text)
        return []


def test_job_specific_exports_endpoint(token: str, job_id: str):
    """Test the new job-specific exports endpoint."""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}{API_VERSION}/exports/files/job/{job_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Job-specific exports endpoint successful")
        print(f"  Job ID: {job_id}")
        print(f"  Total exports: {data['total']}")
        print(f"  Export dates: {list(data['exports_by_date'].keys())}")
        
        # Print exports grouped by date
        for date, exports in data['exports_by_date'].items():
            print(f"\n  Date: {date}")
            print(f"    Count: {len(exports)}")
            for exp in exports:
                print(f"      - {exp['filename']} ({exp['format']})")
        
        return data
    else:
        print(f"❌ Job-specific exports endpoint failed: {response.status_code}")
        print(response.text)
        return None


def main():
    """Run all tests."""
    print("=" * 80)
    print("Testing Job-Specific Exports Endpoint")
    print("=" * 80)
    
    # Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # List all exports
    all_exports = test_list_all_exports(token)
    
    if not all_exports:
        print("\n⚠️ No exports found. Create some exports first:")
        print("   1. Generate a resume/cover letter")
        print("   2. Export it to PDF or DOCX")
        return
    
    # Extract first job_id from exports
    first_job_id = None
    for export in all_exports:
        if export.get('job_id'):
            first_job_id = export['job_id']
            break
    
    if not first_job_id:
        print("\n⚠️ No exports with job_id found.")
        print("   The migration populated job_id for existing exports.")
        print("   Try creating a new export from a generation.")
        return
    
    # Test filtering by job_id
    test_list_exports_with_job_filter(token, first_job_id)
    
    # Test job-specific endpoint
    test_job_specific_exports_endpoint(token, first_job_id)
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
