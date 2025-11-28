"""Test Profile API implementation against documentation - FIXED VERSION."""

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

    print(f"  Register status: {response.status_code}")

    if response.status_code in [400, 409]:
        # User exists (API returns 400 or 409), login instead
        print("  User already exists, attempting login...")
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
        )
        print(f"  Login status: {response.status_code}")

    if response.status_code not in [200, 201]:
        print(f"  [ERROR] Authentication failed: {response.text}")
        raise Exception(f"Authentication failed with status {response.status_code}")

    data = response.json()

    if "access_token" not in data:
        print(f"  [ERROR] Response missing access_token: {json.dumps(data, indent=2)}")
        raise Exception("Missing access_token in response")

    test_data["access_token"] = data["access_token"]
    test_data["user_id"] = data["user"]["id"]
    print(f"  User ID: {test_data['user_id']}")
    print(f"  Token: {test_data['access_token'][:50]}...")
    return test_data["access_token"]


async def test_profile_crud(client: httpx.AsyncClient, token: str):
    """Test Profile CRUD operations (6 endpoints)."""
    print("\n" + "=" * 80)
    print("PROFILE CRUD OPERATIONS (6 endpoints)")
    print("=" * 80)

    headers = {"Authorization": f"Bearer {token}"}

    # Test 1: Create Profile (or get existing)
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
        elif response.status_code == 400 and "already has a profile" in response.text:
            # User already has a profile, get it instead
            print("  User already has a profile, fetching existing profile...")
            response = await client.get(
                f"{BASE_URL}/api/v1/profiles/me",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                test_data["profile_id"] = data["id"]
                print(f"  Profile ID: {data['id']}")
                print("  [PASS] Retrieved existing profile")
            else:
                print(f"  [FAIL] Could not retrieve existing profile: {response.text}")
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
    print(f"\n[TEST 3] GET /api/v1/profiles/{{id}} - Get specific profile...")
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
    print(f"\n[TEST 4] PUT /api/v1/profiles/{{id}} - Update profile...")
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
            f"{BASE_URL}/api/v1/profiles?limit=10&offset=0",
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  Total profiles: {data.get('total', len(data.get('profiles', [])))}")
            print("  [PASS] Listed user profiles")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 6: Profile Analytics
    print(f"\n[TEST 6] GET /api/v1/profiles/{{id}}/analytics - Get profile analytics...")
    try:
        response = await client.get(
            f"{BASE_URL}/api/v1/profiles/{test_data['profile_id']}/analytics",
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  Completeness: {data.get('completeness', {})}")
            print(f"  Statistics: {data.get('statistics', {})}")
            print(f"  Recommendations: {len(data.get('recommendations', []))} items")
            print("  [PASS] Retrieved profile analytics")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")


async def test_experiences_operations(client: httpx.AsyncClient, token: str):
    """Test Experiences bulk operations (4 endpoints)."""
    print("\n" + "=" * 80)
    print("EXPERIENCES OPERATIONS (4 endpoints)")
    print("=" * 80)

    headers = {"Authorization": f"Bearer {token}"}
    profile_id = test_data["profile_id"]

    # Test 7: POST experiences - Add experiences (API expects direct list)
    print(f"\n[TEST 7] POST /api/v1/profiles/{{id}}/experiences - Add experiences...")
    experiences_data = [
        {
            "title": "Senior Software Engineer",
            "company": "TechCorp",
            "location": "Seattle, WA",
            "start_date": "2020-01-15",
            "is_current": True,
            "description": "Led development of microservices architecture using FastAPI and AWS.",
            "achievements": [
                "Reduced API response time by 60%",
                "Led team of 5 engineers",
                "Implemented CI/CD pipeline"
            ]
        },
        {
            "title": "Software Engineer",
            "company": "StartupInc",
            "location": "San Francisco, CA",
            "start_date": "2018-06-01",
            "end_date": "2019-12-31",
            "is_current": False,
            "description": "Full-stack development using React and Node.js.",
            "achievements": ["Built user dashboard", "Implemented real-time chat"]
        }
    ]

    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/experiences",
            json=experiences_data,
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 201:
            data = response.json()
            # API returns list of experiences
            for exp in data:
                test_data["experience_ids"].append(exp["id"])
            print(f"  Added {len(data)} experiences")
            print(f"  Experience IDs: {[exp['id'] for exp in data]}")
            print("  [PASS] Experiences added successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 8: GET experiences
    print(f"\n[TEST 8] GET /api/v1/profiles/{{id}}/experiences - Get all experiences...")
    try:
        response = await client.get(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/experiences",
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            # Response format: {"experiences": [...], "pagination": {...}}
            experiences = data.get("experiences", [])
            print(f"  Total experiences: {len(experiences)}")
            for exp in experiences:
                print(f"    - {exp['title']} at {exp['company']}")
            print("  [PASS] Retrieved all experiences")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 9: PUT experiences - Update experiences (API expects direct list)
    print(f"\n[TEST 9] PUT /api/v1/profiles/{{id}}/experiences - Update experiences...")
    if test_data["experience_ids"]:
        exp_id = test_data["experience_ids"][0]
        updated_experiences = [
            {
                "id": exp_id,
                "title": "Senior Software Engineer",
                "company": "TechCorp",
                "location": "Seattle, WA",
                "start_date": "2020-01-15",
                "is_current": True,
                "description": "Led development of microservices architecture using FastAPI, AWS, and Docker. Mentored junior developers.",
                "achievements": [
                    "Reduced API response time by 60%",
                    "Led team of 5 engineers",
                    "Implemented CI/CD pipeline",
                    "Mentored 3 junior developers"
                ]
            }
        ]

        try:
            response = await client.put(
                f"{BASE_URL}/api/v1/profiles/{profile_id}/experiences",
                json=updated_experiences,
                headers=headers
            )
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"  Updated {len(data)} experiences")
                print("  [PASS] Experiences updated successfully")
            else:
                print(f"  [FAIL] {response.text}")
        except Exception as e:
            print(f"  [FAIL] {e}")

    # Test 10: DELETE experiences
    print(f"\n[TEST 10] DELETE /api/v1/profiles/{{id}}/experiences - Delete experiences...")
    if len(test_data["experience_ids"]) > 1:
        exp_id_to_delete = test_data["experience_ids"][-1]
        delete_data = {"experience_ids": [exp_id_to_delete]}

        try:
            response = await client.request(
                "DELETE",
                f"{BASE_URL}/api/v1/profiles/{profile_id}/experiences",
                json=delete_data,
                headers=headers
            )
            print(f"  Status: {response.status_code}")

            if response.status_code == 204:
                print("  [PASS] Experiences deleted successfully")
            else:
                print(f"  [FAIL] {response.text}")
        except Exception as e:
            print(f"  [FAIL] {e}")


async def test_education_operations(client: httpx.AsyncClient, token: str):
    """Test Education operations (3 endpoints)."""
    print("\n" + "=" * 80)
    print("EDUCATION OPERATIONS (3 endpoints)")
    print("=" * 80)

    headers = {"Authorization": f"Bearer {token}"}
    profile_id = test_data["profile_id"]

    # Test 11: POST education - Add education (API expects direct list)
    print(f"\n[TEST 11] POST /api/v1/profiles/{{id}}/education - Add education...")
    education_data = [
        {
            "institution": "University of Washington",
            "degree": "Bachelor of Science",
            "field_of_study": "Computer Science",
            "start_date": "2012-09-01",
            "end_date": "2016-06-15",
            "gpa": 3.8,
            "honors": ["Magna Cum Laude", "Dean's List"]
        }
    ]

    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/education",
            json=education_data,
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 201:
            data = response.json()
            for edu in data:
                test_data["education_ids"].append(edu["id"])
            print(f"  Added {len(data)} education entries")
            print(f"  Education IDs: {[edu['id'] for edu in data]}")
            print("  [PASS] Education added successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 12: PUT education - Update education
    print(f"\n[TEST 12] PUT /api/v1/profiles/{{id}}/education - Update education...")
    if test_data["education_ids"]:
        edu_id = test_data["education_ids"][0]
        updated_education = [
            {
                "id": edu_id,
                "institution": "University of Washington",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "start_date": "2012-09-01",
                "end_date": "2016-06-15",
                "gpa": 3.9,
                "honors": ["Summa Cum Laude", "Dean's List", "Outstanding Senior Award"]
            }
        ]

        try:
            response = await client.put(
                f"{BASE_URL}/api/v1/profiles/{profile_id}/education",
                json=updated_education,
                headers=headers
            )
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"  Updated {len(data)} education entries")
                print("  [PASS] Education updated successfully")
            else:
                print(f"  [FAIL] {response.text}")
        except Exception as e:
            print(f"  [FAIL] {e}")

    # Test 13: DELETE education
    print(f"\n[TEST 13] DELETE /api/v1/profiles/{{id}}/education - Delete education...")
    if test_data["education_ids"]:
        edu_id = test_data["education_ids"][0]

        try:
            # API expects List[str] directly in body (not wrapped in object)
            response = await client.request(
                "DELETE",
                f"{BASE_URL}/api/v1/profiles/{profile_id}/education",
                headers=headers,
                json=[edu_id]
            )
            print(f"  Status: {response.status_code}")

            if response.status_code in [200, 204]:
                print("  [PASS] Education deleted successfully")
            else:
                print(f"  [FAIL] {response.text}")
        except Exception as e:
            print(f"  [FAIL] {e}")


async def test_projects_operations(client: httpx.AsyncClient, token: str):
    """Test Projects operations (3 endpoints)."""
    print("\n" + "=" * 80)
    print("PROJECTS OPERATIONS (3 endpoints)")
    print("=" * 80)

    headers = {"Authorization": f"Bearer {token}"}
    profile_id = test_data["profile_id"]

    # Test 14: POST projects - Add projects (API expects direct list)
    print(f"\n[TEST 14] POST /api/v1/profiles/{{id}}/projects - Add projects...")
    projects_data = [
        {
            "name": "JobWise AI",
            "description": "AI-powered job application assistant built with Flutter and FastAPI.",
            "technologies": ["Flutter", "FastAPI", "PostgreSQL", "Docker", "AWS"],
            "url": "https://github.com/johndoe/jobwise",
            "start_date": "2025-01-01",
            "end_date": "2025-11-01"
        }
    ]

    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/profiles/{profile_id}/projects",
            json=projects_data,
            headers=headers
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 201:
            data = response.json()
            for proj in data:
                test_data["project_ids"].append(proj["id"])
            print(f"  Added {len(data)} projects")
            print(f"  Project IDs: {[proj['id'] for proj in data]}")
            print("  [PASS] Projects added successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 15: PUT projects - Update projects
    print(f"\n[TEST 15] PUT /api/v1/profiles/{{id}}/projects - Update projects...")
    if test_data["project_ids"]:
        proj_id = test_data["project_ids"][0]
        updated_projects = [
            {
                "id": proj_id,
                "name": "JobWise AI",
                "description": "AI-powered job application assistant with resume and cover letter generation using Groq LLM.",
                "technologies": ["Flutter", "FastAPI", "PostgreSQL", "Docker", "AWS", "Groq"],
                "url": "https://github.com/johndoe/jobwise",
                "start_date": "2025-01-01",
                "end_date": "2025-11-01"
            }
        ]

        try:
            response = await client.put(
                f"{BASE_URL}/api/v1/profiles/{profile_id}/projects",
                json=updated_projects,
                headers=headers
            )
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"  Updated {len(data)} projects")
                print("  [PASS] Projects updated successfully")
            else:
                print(f"  [FAIL] {response.text}")
        except Exception as e:
            print(f"  [FAIL] {e}")

    # Test 16: DELETE projects
    print(f"\n[TEST 16] DELETE /api/v1/profiles/{{id}}/projects - Delete projects...")
    if test_data["project_ids"]:
        proj_id = test_data["project_ids"][0]

        try:
            # API expects List[str] directly in body (not wrapped in object)
            response = await client.request(
                "DELETE",
                f"{BASE_URL}/api/v1/profiles/{profile_id}/projects",
                headers=headers,
                json=[proj_id]
            )
            print(f"  Status: {response.status_code}")

            if response.status_code in [200, 204]:
                print("  [PASS] Projects deleted successfully")
            else:
                print(f"  [FAIL] {response.text}")
        except Exception as e:
            print(f"  [FAIL] {e}")


async def test_skills_management(client: httpx.AsyncClient, token: str):
    """Test Skills management (6 endpoints)."""
    print("\n" + "=" * 80)
    print("SKILLS MANAGEMENT (6 endpoints)")
    print("=" * 80)

    headers = {"Authorization": f"Bearer {token}"}
    profile_id = test_data["profile_id"]

    # Test 17: GET skills
    print(f"\n[TEST 17] GET /api/v1/profiles/{{id}}/skills - Get all skills...")
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

    # Test 18: POST technical skills
    print(f"\n[TEST 18] POST /api/v1/profiles/{{id}}/skills/technical - Add technical skills...")
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
            print(f"  Message: {data.get('message', 'Skills added')}")
            print("  [PASS] Technical skills added successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 19: POST soft skills
    print(f"\n[TEST 19] POST /api/v1/profiles/{{id}}/skills/soft - Add soft skills...")
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
            print(f"  Message: {data.get('message', 'Skills added')}")
            print("  [PASS] Soft skills added successfully")
        else:
            print(f"  [FAIL] {response.text}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Test 20: PUT all skills
    print(f"\n[TEST 20] PUT /api/v1/profiles/{{id}}/skills - Update all skills...")
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

    # Test 21: DELETE technical skills
    print(f"\n[TEST 21] DELETE /api/v1/profiles/{{id}}/skills/technical - Delete technical skills...")
    delete_skills_data = {"skills": ["GraphQL"]}

    try:
        response = await client.request(
            "DELETE",
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

    # Test 22: DELETE soft skills
    print(f"\n[TEST 22] DELETE /api/v1/profiles/{{id}}/skills/soft - Delete soft skills...")
    delete_soft_skills_data = {"skills": ["Conflict Resolution"]}

    try:
        response = await client.request(
            "DELETE",
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
    print("CUSTOM FIELDS OPERATIONS (2 endpoints)")
    print("=" * 80)

    headers = {"Authorization": f"Bearer {token}"}
    profile_id = test_data["profile_id"]

    # Test 23: GET custom fields
    print(f"\n[TEST 23] GET /api/v1/profiles/{{id}}/custom-fields - Get custom fields...")
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

    # Test 24: PUT custom fields
    print(f"\n[TEST 24] PUT /api/v1/profiles/{{id}}/custom-fields - Update custom fields...")
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
    print("PROFILE API TESTING - FIXED VERSION")
    print("=" * 80)

    test_results = {
        "total": 24,
        "passed": 0,
        "failed": 0
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
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
