import asyncio
import httpx

async def debug_test():
    async with httpx.AsyncClient(base_url='http://localhost:8000', timeout=30.0) as client:
        # Generate unique email
        import time
        timestamp = int(time.time() * 1000)
        email = f"debug_{timestamp}@example.com"

        user_data = {
            "email": email,
            "password": "SecurePass123!",
            "full_name": "Debug User"
        }

        # Register user
        register_response = await client.post("/api/v1/auth/register", json=user_data)
        access_token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create profile
        profile_data = {
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

        create_response = await client.post("/api/v1/profiles", json=profile_data, headers=headers)
        profile_id = create_response.json()["id"]

        # Update skills
        updated_skills = {
            "technical": ["Python", "Go", "Rust", "Docker"],
            "soft": ["Leadership", "Mentoring"],
            "languages": [
                {"name": "English", "proficiency": "native"},
                {"name": "French", "proficiency": "intermediate"},
                {"name": "Japanese", "proficiency": "beginner"}
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

        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(debug_test())