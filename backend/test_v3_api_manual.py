"""Test V3 API endpoints with real HTTP requests."""

import asyncio
import httpx
import json
from pathlib import Path


async def test_v3_api_endpoints():
    """Test sample upload endpoints with real files."""
    
    base_url = "http://localhost:8000"
    
    # First, we need to register and login
    print("=" * 60)
    print("V3 API Endpoint Tests")
    print("=" * 60)
    
    # Register user
    print("\n1️⃣ Registering test user...")
    async with httpx.AsyncClient() as client:
        register_response = await client.post(
            f"{base_url}/api/v1/auth/register",
            json={
                "email": "testv3@example.com",
                "password": "TestPassword123!",
                "name": "Test V3 User"
            }
        )
        
        if register_response.status_code == 201:
            print("✅ User registered successfully")
        elif register_response.status_code == 409:
            print("ℹ️ User already exists")
        else:
            print(f"⚠️ Registration status: {register_response.status_code}")
    
    # Login
    print("\n2️⃣ Logging in...")
    async with httpx.AsyncClient() as client:
        login_response = await client.post(
            f"{base_url}/api/v1/auth/login",
            json={
                "email": "testv3@example.com",
                "password": "TestPassword123!"
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
        
        token = login_response.json()["access_token"]
        print(f"✅ Logged in successfully")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Upload resume
    print("\n3️⃣ Testing POST /api/v1/samples/upload (resume)...")
    resume_path = Path(__file__).parent.parent / "docs" / "sample artifacts" / "Huy_Ky_Enhanced_Resume.txt"
    
    async with httpx.AsyncClient() as client:
        with open(resume_path, "rb") as f:
            files = {"file": ("Huy_Ky_Enhanced_Resume.txt", f, "text/plain")}
            data = {"document_type": "resume"}
            
            response = await client.post(
                f"{base_url}/api/v1/samples/upload",
                headers=headers,
                files=files,
                data=data
            )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Resume uploaded successfully")
            print(f"   ID: {result['id']}")
            print(f"   Words: {result['word_count']}")
            print(f"   Characters: {result['character_count']}")
            resume_id = result['id']
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.text)
            return
    
    # Test 2: Upload cover letter
    print("\n4️⃣ Testing POST /api/v1/samples/upload (cover letter)...")
    cover_letter_path = Path(__file__).parent.parent / "docs" / "sample artifacts" / "Huy_Ky_General_Cover_Letter.txt"
    
    async with httpx.AsyncClient() as client:
        with open(cover_letter_path, "rb") as f:
            files = {"file": ("Huy_Ky_General_Cover_Letter.txt", f, "text/plain")}
            data = {"document_type": "cover_letter"}
            
            response = await client.post(
                f"{base_url}/api/v1/samples/upload",
                headers=headers,
                files=files,
                data=data
            )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Cover letter uploaded successfully")
            print(f"   ID: {result['id']}")
            print(f"   Words: {result['word_count']}")
            print(f"   Characters: {result['character_count']}")
            cover_letter_id = result['id']
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.text)
            return
    
    # Test 3: Get samples list
    print("\n5️⃣ Testing GET /api/v1/samples...")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/api/v1/samples",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved {result['total']} samples")
            for sample in result['samples']:
                print(f"   - {sample['document_type']}: {sample['original_filename']}")
        else:
            print(f"❌ Get failed: {response.status_code}")
    
    # Test 4: Get sample detail
    print(f"\n6️⃣ Testing GET /api/v1/samples/{resume_id}...")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/api/v1/samples/{resume_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved sample detail")
            print(f"   Filename: {result['original_filename']}")
            print(f"   Text length: {len(result['original_text'])} chars")
            print(f"   First 100 chars: {result['original_text'][:100]}...")
        else:
            print(f"❌ Get detail failed: {response.status_code}")
    
    # Test 5: Filter by document type
    print("\n7️⃣ Testing GET /api/v1/samples?document_type=resume...")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/api/v1/samples?document_type=resume",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved {result['total']} resume samples")
        else:
            print(f"❌ Filter failed: {response.status_code}")
    
    # Test 6: Invalid file type
    print("\n8️⃣ Testing invalid file type (should return 400)...")
    async with httpx.AsyncClient() as client:
        files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
        data = {"document_type": "resume"}
        
        response = await client.post(
            f"{base_url}/api/v1/samples/upload",
            headers=headers,
            files=files,
            data=data
        )
        
        if response.status_code == 400:
            print(f"✅ Correctly rejected non-.txt file")
            print(f"   Error: {response.json()['detail']}")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ All API tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_v3_api_endpoints())
