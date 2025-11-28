"""Test Profile API implementation against documentation."""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any


BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "profiletest@example.com",
    "password": "SecurePass123",
    "full_name": "Profile Test User"
}

# Global storage for test data
test_data: Dict[str, Any] = {
    "access_token": None,
    "user_id": None,
    "profile_id": None,
    "experience_ids": [],
    "education_ids": [],
    "project_ids": []
}


async def setup_test_user(client: httpx.AsyncClient) -> str:
    """Create test user and get access token."""
    print("\n[SETUP] Creating test user and obtaining access token...")

    # Try to register
    response = await client.post(
        f"{BASE_URL}/api/v1/auth/register",
        json=TEST_USER
    )

    if response.status_code == 409:
        # User exists, login instead
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
        )

    data = response.json()
    test_data["access_token"] = data["access_token"]
    test_data["user_id"] = data["user"]["id"]
    print(f"  User ID: {test_data['user_id']}")
    print(f"  Token: {test_data['access_token'][:50]}...")
    return test_data["access_token"]


async def test_profile_crud(client: httpx.AsyncClient, token: str):
    """Test Profile CRUD operations (6 endpoints)."""
    print("\n" + "=" * 80)
    print("PROFILE CRUD OPERATIONS")
    print("=" * 80)

    headers = {"Authorization": f"Bearer {token}"}

    # Test 1: Create Profile
    print("\n[TEST 1] POST /api/v1/profiles - Create new profile...")
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
        "professional_summary": "Senior Software Engineer with 8+ years of experience in full-stack development.",
        "skills": {
            "technical": ["Python", "FastAPI", "React", "AWS"],
            "soft": ["Leadership", "Communication", "Problem Solving"],
            "languages": [
                {"name": "English", "proficiency": "native"},
                {"name": "Spanish", "proficiency": "conversational"}
            ],
            "certifications": [
                {
                    "name": "AWS Solutions Architect",
                    "issuer": "Amazon",
                    "date_obtained": "2023-01-15",
                    "credential_id": "AWS-SA-123"
                }
            ]
        },
        "custom_fields": {
            "portfolio_url": "https://portfolio.johndoe.com",
            "preferred_location": "Remote, USA"
        }
    }

    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/profiles",
            json=profile_data,
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 201:
            data = response.json()
            test_data["profile_id"] = data["id"]
            print(f"  Profile ID: {data['id']}")
            print(f"  User ID: {data['user_id']}")
            print(f"  Full Name: {data['personal_info']['full_name']}")
            print(f"  Skills: {len(data['skills']['technical'])} technical, {len(data['skills']['soft'])} soft")
            print("  [PASS] Profile created successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 2: Get Primary Profile
    print("\n[TEST 2] GET /api/v1/profiles/me - Get primary profile...")
    try:
        response = await client.get(
            f"{BASE_URL}/api/v1/profiles/me",
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  Profile ID: {data['id']}")
            print(f"  Professional Summary: {data['professional_summary'][:50]}...")
            print("  [PASS] Retrieved primary profile")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 3: Get Specific Profile
    print(f"\n[TEST 3] GET /api/v1/profiles/{test_data['profile_id']} - Get specific profile...")
    try:
        response = await client.get(
            f"{BASE_URL}/api/v1/profiles/{test_data['profile_id']}",
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  Retrieved profile: {data['personal_info']['full_name']}")
            print("  [PASS] Retrieved specific profile")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 4: Update Profile
    print(f"\n[TEST 4] PUT /api/v1/profiles/{test_data['profile_id']} - Update profile...")
    update_data = {
        "professional_summary": "Senior Software Engineer with 9+ years of experience in full-stack development and cloud architecture."
    }

    try:
        response = await client.put(
            f"{BASE_URL}/api/v1/profiles/{test_data['profile_id']}",
            json=update_data,
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  Updated summary: {data['professional_summary'][:60]}...")
            print("  [PASS] Profile updated successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 5: List User Profiles
    print("\n[TEST 5] GET /api/v1/profiles - List all user profiles...")
    try:
        response = await client.get(
            f"{BASE_URL}/api/v1/profiles",
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  Total profiles: {len(data)}")
            print("  [PASS] Listed user profiles")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 6: Profile Analytics
    print(f"\n[TEST 6] GET /api/v1/profiles/{test_data['profile_id']}/analytics - Get profile analytics...")
    try:
        response = await client.get(
            f"{BASE_URL}/api/v1/profiles/{test_data['profile_id']}/analytics",
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  Completeness Score: {data.get('completeness_score', 'N/A')}%")
            print(f"  Missing Sections: {data.get('missing_sections', [])}")
            print("  [PASS] Retrieved profile analytics")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")


async def test_experiences_operations(client: httpx.AsyncClient, token: str):
    """Test Experiences bulk operations (4 endpoints)."""
    print("\n" + "=" * 80)
    print("EXPERIENCES OPERATIONS")
    print("=" * 80)

    headers = {"Authorization": f"Bearer {token}"}
    profile_id = test_data["profile_id"]

    # Test 1: Add Single Experience
    print(f"\n[TEST 7] POST /api/v1/profiles/{profile_id}/experiences - Add single experience...")
    experience_data = {
        "experience": {
            "title": "Senior Software Engineer",
            "company": "TechCorp",
            "location": "Seattle, WA",
            "start_date": "2020-01-15",
            "end_date": None,
            "is_current": True,
            "description": "Led development of microservices architecture using FastAPI and AWS.",
            "achievements": [
                "Reduced API response time by 60%",
                "Led team of 5 engineers",
                "Implemented CI/CD pipeline"
            ]
        }
    }

    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/experiences",
            json=experience_data,
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 201:
            data = response.json()
            test_data["experience_ids"].append(data["id"])
            print(f"  Experience ID: {data['id']}")
            print(f"  Title: {data['title']} at {data['company']}")
            print(f"  Current: {data['is_current']}")
            print("  [PASS] Experience added successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 2: Add Bulk Experiences
    print(f"\n[TEST 8] POST /api/v1/profiles/{profile_id}/experiences (bulk) - Add multiple experiences...")
    bulk_experiences = {
        "experiences": [
            {
                "title": "Software Engineer",
                "company": "StartupInc",
                "location": "San Francisco, CA",
                "start_date": "2018-06-01",
                "end_date": "2019-12-31",
                "is_current": False,
                "description": "Full-stack development using React and Node.js.",
                "achievements": ["Built user dashboard", "Implemented real-time chat"]
            },
            {
                "title": "Junior Developer",
                "company": "CodeFactory",
                "location": "Austin, TX",
                "start_date": "2016-01-01",
                "end_date": "2018-05-31",
                "is_current": False,
                "description": "Backend development with Python and Django.",
                "achievements": ["Developed REST API", "Improved database performance"]
            }
        ]
    }

    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/experiences/bulk",
            json=bulk_experiences,
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 201:
            data = response.json()
            for exp in data:
                test_data["experience_ids"].append(exp["id"])
            print(f"  Added {len(data)} experiences")
            print("  [PASS] Bulk experiences added successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 3: Get All Experiences
    print(f"\n[TEST 9] GET /api/v1/profiles/{profile_id}/experiences - Get all experiences...")
    try:
        response = await client.get(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/experiences",
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  Total experiences: {len(data)}")
            for exp in data:
                print(f"    - {exp['title']} at {exp['company']}")
            print("  [PASS] Retrieved all experiences")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 4: Update Experience
    print(f"\n[TEST 10] PUT /api/v1/profiles/{profile_id}/experiences - Update experience...")
    if test_data["experience_ids"]:
        exp_id = test_data["experience_ids"][0]
        update_data = {
            "experience": {
                "id": exp_id,
                "description": "Led development of microservices architecture using FastAPI, AWS, and Docker. Mentored junior developers."
            }
        }

        try:
            response = await client.put(
                f"{BASE_URL}/api/v1/profiles/{profile_id}/experiences",
                json=update_data,
                headers=headers
            )
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                print("  [PASS] Experience updated successfully")
            else:
                print(f"  [FAIL] {response.text}")
        except Exception as e:
            print(f"  [FAIL] {e}")


async def test_education_operations(client: httpx.AsyncClient, token: str):
    """Test Education operations (3 endpoints)."""
    print("\n" + "=" * 80)
    print("EDUCATION OPERATIONS")
    print("=" * 80)

    headers = {"Authorization": f"Bearer {token}"}
    profile_id = test_data["profile_id"]

    # Test 1: Add Education
    print(f"\n[TEST 11] POST /api/v1/profiles/{profile_id}/education - Add education...")
    education_data = {
        "education": {
            "institution": "University of Washington",
            "degree": "Bachelor of Science",
            "field_of_study": "Computer Science",
            "start_date": "2012-09-01",
            "end_date": "2016-06-15",
            "gpa": 3.8,
            "honors": ["Magna Cum Laude", "Dean's List"]
        }
    }

    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/education",
            json=education_data,
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 201:
            data = response.json()
            test_data["education_ids"].append(data["id"])
            print(f"  Education ID: {data['id']}")
            print(f"  Degree: {data['degree']} in {data['field_of_study']}")
            print(f"  Institution: {data['institution']}")
            print(f"  GPA: {data.get('gpa', 'N/A')}")
            print("  [PASS] Education added successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 2: Get All Education
    print(f"\n[TEST 12] GET /api/v1/profiles/{profile_id}/education - Get all education...")
    try:
        response = await client.get(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/education",
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  Total education entries: {len(data)}")
            print("  [PASS] Retrieved all education")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 3: Delete Education
    print(f"\n[TEST 13] DELETE /api/v1/profiles/{profile_id}/education - Delete education...")
    if test_data["education_ids"]:
        edu_id = test_data["education_ids"][0]
        delete_data = {"education_ids": [edu_id]}

        try:
            response = await client.delete(
                f"{BASE_URL}/api/v1/profiles/{profile_id}/education",
                json=delete_data,
                headers=headers
            )
            print(f"  Status: {response.status_code}")

            if response.status_code == 204:
                print("  [PASS] Education deleted successfully")
            else:
                print(f"  [FAIL] {response.text}")
        except Exception as e:
            print(f"  [FAIL] {e}")


async def test_projects_operations(client: httpx.AsyncClient, token: str):
    """Test Projects operations (3 endpoints)."""
    print("\n" + "=" * 80)
    print("PROJECTS OPERATIONS")
    print("=" * 80)

    headers = {"Authorization": f"Bearer {token}"}
    profile_id = test_data["profile_id"]

    # Test 1: Add Project
    print(f"\n[TEST 14] POST /api/v1/profiles/{profile_id}/projects - Add project...")
    project_data = {
        "project": {
            "name": "JobWise AI",
            "description": "AI-powered job application assistant built with Flutter and FastAPI.",
            "technologies": ["Flutter", "FastAPI", "PostgreSQL", "Docker", "AWS"],
            "url": "https://github.com/johndoe/jobwise",
            "start_date": "2025-01-01",
            "end_date": "2025-11-01"
        }
    }

    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/projects",
            json=project_data,
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 201:
            data = response.json()
            test_data["project_ids"].append(data["id"])
            print(f"  Project ID: {data['id']}")
            print(f"  Name: {data['name']}")
            print(f"  Technologies: {', '.join(data.get('technologies', []))}")
            print("  [PASS] Project added successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 2: Get All Projects
    print(f"\n[TEST 15] GET /api/v1/profiles/{profile_id}/projects - Get all projects...")
    try:
        response = await client.get(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/projects",
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  Total projects: {len(data)}")
            print("  [PASS] Retrieved all projects")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 3: Update Project
    print(f"\n[TEST 16] PUT /api/v1/profiles/{profile_id}/projects - Update project...")
    if test_data["project_ids"]:
        proj_id = test_data["project_ids"][0]
        update_data = {
            "project": {
                "id": proj_id,
                "description": "AI-powered job application assistant with resume and cover letter generation using Groq LLM."
            }
        }

        try:
            response = await client.put(
                f"{BASE_URL}/api/v1/profiles/{profile_id}/projects",
                json=update_data,
                headers=headers
            )
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                print("  [PASS] Project updated successfully")
            else:
                print(f"  [FAIL] {response.text}")
        except Exception as e:
            print(f"  [FAIL] {e}")


async def test_skills_management(client: httpx.AsyncClient, token: str):
    """Test Skills management (6 endpoints)."""
    print("\n" + "=" * 80)
    print("SKILLS MANAGEMENT")
    print("=" * 80)

    headers = {"Authorization": f"Bearer {token}"}
    profile_id = test_data["profile_id"]

    # Test 1: Get Skills
    print(f"\n[TEST 17] GET /api/v1/profiles/{profile_id}/skills - Get all skills...")
    try:
        response = await client.get(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/skills",
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  Technical: {len(data.get('technical', []))} skills")
            print(f"  Soft: {len(data.get('soft', []))} skills")
            print("  [PASS] Retrieved all skills")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 2: Add Technical Skills
    print(f"\n[TEST 18] POST /api/v1/profiles/{profile_id}/skills/technical - Add technical skills...")
    skills_data = {"skills": ["Kubernetes", "Terraform", "GraphQL"]}

    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/skills/technical",
            json=skills_data,
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  Total technical skills: {len(data.get('technical', []))}")
            print("  [PASS] Technical skills added successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 3: Add Soft Skills
    print(f"\n[TEST 19] POST /api/v1/profiles/{profile_id}/skills/soft - Add soft skills...")
    soft_skills_data = {"skills": ["Team Building", "Conflict Resolution"]}

    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/skills/soft",
            json=soft_skills_data,
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  Total soft skills: {len(data.get('soft', []))}")
            print("  [PASS] Soft skills added successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 4: Update All Skills
    print(f"\n[TEST 20] PUT /api/v1/profiles/{profile_id}/skills - Update all skills...")
    all_skills_data = {
        "technical": ["Python", "FastAPI", "React", "AWS", "Docker", "Kubernetes"],
        "soft": ["Leadership", "Communication", "Problem Solving", "Team Building"],
        "languages": [
            {"name": "English", "proficiency": "native"},
            {"name": "Spanish", "proficiency": "conversational"}
        ],
        "certifications": [
            {
                "name": "AWS Solutions Architect",
                "issuer": "Amazon",
                "date_obtained": "2023-01-15",
                "credential_id": "AWS-SA-123"
            }
        ]
    }

    try:
        response = await client.put(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/skills",
            json=all_skills_data,
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            print("  [PASS] All skills updated successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 5: Delete Technical Skills
    print(f"\n[TEST 21] DELETE /api/v1/profiles/{profile_id}/skills/technical - Delete technical skills...")
    delete_skills_data = {"skills": ["GraphQL"]}

    try:
        response = await client.delete(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/skills/technical",
            json=delete_skills_data,
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            print("  [PASS] Technical skills deleted successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 6: Delete Soft Skills
    print(f"\n[TEST 22] DELETE /api/v1/profiles/{profile_id}/skills/soft - Delete soft skills...")
    delete_soft_skills_data = {"skills": ["Conflict Resolution"]}

    try:
        response = await client.delete(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/skills/soft",
            json=delete_soft_skills_data,
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            print("  [PASS] Soft skills deleted successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")


async def test_custom_fields(client: httpx.AsyncClient, token: str):
    """Test Custom Fields operations (2 endpoints)."""
    print("\n" + "=" * 80)
    print("CUSTOM FIELDS OPERATIONS")
    print("=" * 80)

    headers = {"Authorization": f"Bearer {token}"}
    profile_id = test_data["profile_id"]

    # Test 1: Get Custom Fields
    print(f"\n[TEST 23] GET /api/v1/profiles/{profile_id}/custom-fields - Get custom fields...")
    try:
        response = await client.get(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/custom-fields",
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  Custom fields: {json.dumps(data, indent=2)}")
            print("  [PASS] Retrieved custom fields")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 2: Update Custom Fields
    print(f"\n[TEST 24] PUT /api/v1/profiles/{profile_id}/custom-fields - Update custom fields...")
    custom_fields_data = {
        "portfolio_url": "https://newportfolio.johndoe.com",
        "preferred_location": "Remote, Worldwide",
        "salary_expectation": "$140k-$180k",
        "availability": "2 weeks notice"
    }

    try:
        response = await client.put(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/custom-fields",
            json=custom_fields_data,
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            print("  [PASS] Custom fields updated successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")


async def test_profile_api():
    """Run all Profile API tests."""
    print("=" * 80)
    print("PROFILE API TESTING")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        # Setup
        token = await setup_test_user(client)

        # Run all tests
        await test_profile_crud(client, token)
        await test_experiences_operations(client, token)
        await test_education_operations(client, token)
        await test_projects_operations(client, token)
        await test_skills_management(client, token)
        await test_custom_fields(client, token)

        print("\n" + "=" * 80)
        print("PROFILE API TESTING COMPLETE")
        print("=" * 80)
        print(f"\nTest Data Summary:")
        print(f"  Profile ID: {test_data['profile_id']}")
        print(f"  Experiences: {len(test_data['experience_ids'])} created")
        print(f"  Education: {len(test_data['education_ids'])} created")
        print(f"  Projects: {len(test_data['project_ids'])} created")


if __name__ == "__main__":
    print("\nStarting Profile API tests...")
    print("Make sure the server is running: python -m uvicorn app.main:app --reload\n")
    asyncio.run(test_profile_api())
