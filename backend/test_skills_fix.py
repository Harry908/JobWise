import asyncio
import httpx

async def test_skills_update():
    async with httpx.AsyncClient(base_url='http://localhost:8000', timeout=30.0) as client:
        # Generate unique email
        import time
        timestamp = int(time.time() * 1000)
        email = f"test_skills_{timestamp}@example.com"

        user_data = {
            "email": email,
            "password": "SecurePass123!",
            "full_name": "Test User"
        }

        # Register user
        register_response = await client.post("/api/v1/auth/register", json=user_data)
        print(f"Register status: {register_response.status_code}")
        if register_response.status_code != 201:
            print(f"Register error: {register_response.text}")
            return

        access_token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create profile
        profile_data = {
            "personal_info": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "phone": "+1-555-123-4567",
                "location": "Seattle, WA"
            },
            "professional_summary": "Test summary",
            "skills": {
                "technical": ["Python"],
                "soft": ["Leadership"],
                "languages": [{"name": "English", "proficiency": "native"}],
                "certifications": []
            }
        }

        create_response = await client.post("/api/v1/profiles", json=profile_data, headers=headers)
        print(f"Create profile status: {create_response.status_code}")
        if create_response.status_code != 201:
            print(f"Create error: {create_response.text}")
            return

        profile_id = create_response.json()["id"]
        print(f"Created profile: {profile_id}")

        # Update skills with corrected proficiency values
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

        response = await client.put(
            f"/api/v1/profiles/{profile_id}/skills",
            json=updated_skills,
            headers=headers
        )

        print(f"Update skills status: {response.status_code}")
        if response.status_code != 200:
            print(f"Update error: {response.text}")
        else:
            print("Skills updated successfully!")
            print(f"Response: {response.json()}")

if __name__ == "__main__":
    asyncio.run(test_skills_update())