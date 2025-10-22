"""Live server tests for profile bulk operations and granular component CRUD."""

import time
import pytest
from httpx import AsyncClient


class TestProfileBulkOperationsLive:
    """Live server test suite for profile bulk operations."""

    @pytest.fixture
    def live_client(self):
        """Create HTTP client for live server testing."""
        return AsyncClient(base_url="http://localhost:8000", timeout=30.0)

    def _generate_unique_email(self, prefix: str = "test") -> str:
        """Generate unique email using timestamp to avoid duplicates."""
        timestamp = int(time.time() * 1000)
        return f"{prefix}_{timestamp}@example.com"

    def _generate_unique_user_data(self, prefix: str = "test"):
        """Generate unique test user data."""
        email = self._generate_unique_email(prefix)
        return {
            "email": email,
            "password": "SecurePass123!",
            "full_name": f"Test User {prefix}"
        }

    async def _get_auth_headers(self, live_client: AsyncClient, user_data: dict) -> dict:
        """Helper to register user and get auth headers."""
        register_response = await live_client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        access_token = register_response.json()["access_token"]
        return {"Authorization": f"Bearer {access_token}"}

    def _get_sample_profile_data(self):
        """Get sample profile creation data."""
        return {
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

    def _get_sample_experiences(self):
        """Get sample experiences data for bulk operations."""
        return [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "location": "Seattle, WA",
                "start_date": "2021-01-01",
                "end_date": "2023-06-01",
                "is_current": False,
                "description": "Led development of microservices architecture",
                "achievements": [
                    "Improved system performance by 40%",
                    "Led team of 4 developers"
                ]
            },
            {
                "title": "Software Engineer",
                "company": "Startup Inc",
                "location": "San Francisco, CA",
                "start_date": "2019-01-01",
                "end_date": "2020-12-31",
                "is_current": False,
                "description": "Full-stack development using React and Node.js",
                "achievements": [
                    "Built user-facing features",
                    "Improved application performance"
                ]
            }
        ]

    def _get_sample_education(self):
        """Get sample education data for bulk operations."""
        return [
            {
                "institution": "University of Washington",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "start_date": "2015-09-01",
                "end_date": "2019-06-15",
                "gpa": 3.8,
                "honors": ["Dean's List", "Summa Cum Laude"]
            },
            {
                "institution": "Stanford University",
                "degree": "Master of Science",
                "field_of_study": "Software Engineering",
                "start_date": "2019-09-01",
                "end_date": "2021-06-15",
                "gpa": 3.9,
                "honors": ["Graduate Research Assistant", "Teaching Assistant"]
            }
        ]

    def _get_sample_projects(self):
        """Get sample projects data for bulk operations."""
        return [
            {
                "name": "E-commerce Platform",
                "description": "Built scalable e-commerce solution with React and Node.js",
                "technologies": ["React", "Node.js", "PostgreSQL", "AWS"],
                "url": "https://github.com/johndoe/ecommerce",
                "start_date": "2020-01-01",
                "end_date": "2020-12-31"
            },
            {
                "name": "AI Chat Application",
                "description": "Real-time chat application with AI-powered responses",
                "technologies": ["Python", "FastAPI", "WebSocket", "OpenAI API"],
                "url": "https://github.com/johndoe/ai-chat",
                "start_date": "2021-03-01",
                "end_date": "2021-08-01"
            },
            {
                "name": "Mobile Fitness Tracker",
                "description": "Cross-platform mobile app for fitness tracking",
                "technologies": ["Flutter", "Firebase", "Dart"],
                "url": "https://github.com/johndoe/fitness-tracker",
                "start_date": "2022-01-01",
                "end_date": "2022-06-01"
            }
        ]

    @pytest.mark.asyncio
    async def test_bulk_create_experiences_success(self, live_client: AsyncClient):
        """Test successful bulk creation of work experiences."""
        user_data = self._generate_unique_user_data("bulk_exp")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()
        experiences_data = self._get_sample_experiences()

        # Create profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Bulk create experiences
        response = await live_client.post(
            f"/api/v1/profiles/{profile_id}/experiences",
            json=experiences_data,
            headers=headers
        )

        assert response.status_code == 201
        data = response.json()

        # Check response structure
        assert isinstance(data, list)
        assert len(data) == 2

        # Check first experience
        exp1 = data[0]
        assert "id" in exp1
        assert exp1["title"] == "Senior Software Engineer"
        assert exp1["company"] == "Tech Corp"
        assert exp1["is_current"] is False
        assert len(exp1["achievements"]) == 2

        # Check second experience
        exp2 = data[1]
        assert "id" in exp2
        assert exp2["title"] == "Software Engineer"
        assert exp2["company"] == "Startup Inc"
        assert exp2["is_current"] is False

    @pytest.mark.asyncio
    async def test_bulk_create_experiences_unauthorized(self, live_client: AsyncClient):
        """Test bulk creation of experiences fails without authentication."""
        experiences_data = self._get_sample_experiences()

        response = await live_client.post(
            "/api/v1/profiles/profile-123/experiences",
            json=experiences_data
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_bulk_create_experiences_wrong_owner(self, live_client: AsyncClient):
        """Test bulk creation of experiences fails when accessing another user's profile."""
        # Create first user and profile
        user1_data = self._generate_unique_user_data("user1_exp")
        headers1 = await self._get_auth_headers(live_client, user1_data)
        profile_data = self._get_sample_profile_data()

        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers1)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Create second user
        user2_data = self._generate_unique_user_data("user2_exp")
        headers2 = await self._get_auth_headers(live_client, user2_data)
        experiences_data = self._get_sample_experiences()

        # Try to add experiences to first user's profile
        response = await live_client.post(
            f"/api/v1/profiles/{profile_id}/experiences",
            json=experiences_data,
            headers=headers2
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_bulk_create_experiences_invalid_data(self, live_client: AsyncClient):
        """Test bulk creation of experiences fails with invalid data."""
        user_data = self._generate_unique_user_data("invalid_exp")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()

        # Create profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Try to create experiences with invalid data
        invalid_experiences = [
            {
                "title": "",  # Invalid: empty title
                "company": "Test Company",
                "start_date": "invalid-date"  # Invalid: bad date format
            }
        ]

        response = await live_client.post(
            f"/api/v1/profiles/{profile_id}/experiences",
            json=invalid_experiences,
            headers=headers
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_bulk_update_experiences_success(self, live_client: AsyncClient):
        """Test successful bulk update of work experiences."""
        user_data = self._generate_unique_user_data("update_exp")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()
        experiences_data = self._get_sample_experiences()

        # Create profile and experiences first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        create_exp_response = await live_client.post(
            f"/api/v1/profiles/{profile_id}/experiences",
            json=experiences_data,
            headers=headers
        )
        assert create_exp_response.status_code == 201
        created_experiences = create_exp_response.json()

        # Update experiences with IDs
        update_data = [
            {
                "id": created_experiences[0]["id"],
                "title": "Principal Software Engineer",
                "company": "Tech Corp",
                "location": "Seattle, WA",
                "start_date": "2021-01-01",
                "end_date": "2023-12-01",
                "is_current": False,
                "description": "Led development of microservices and cloud infrastructure",
                "achievements": [
                    "Improved system performance by 40%",
                    "Led team of 4 developers",
                    "Implemented CI/CD pipeline"
                ]
            },
            {
                "id": created_experiences[1]["id"],
                "title": "Senior Software Engineer",
                "company": "Startup Inc",
                "location": "San Francisco, CA",
                "start_date": "2019-01-01",
                "end_date": "2020-12-31",
                "is_current": False,
                "description": "Full-stack development and team leadership",
                "achievements": [
                    "Built user-facing features",
                    "Improved application performance",
                    "Mentored junior developers"
                ]
            }
        ]

        response = await live_client.put(
            f"/api/v1/profiles/{profile_id}/experiences",
            json=update_data,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert isinstance(data, list)
        assert len(data) == 2

        # Check updated experiences
        assert data[0]["title"] == "Principal Software Engineer"
        assert data[0]["company"] == "Tech Corp"
        assert len(data[0]["achievements"]) == 3

        assert data[1]["title"] == "Senior Software Engineer"
        assert data[1]["company"] == "Startup Inc"

    @pytest.mark.asyncio
    async def test_bulk_delete_experiences_success(self, live_client: AsyncClient):
        """Test successful bulk deletion of work experiences."""
        user_data = self._generate_unique_user_data("delete_exp")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()
        experiences_data = self._get_sample_experiences()

        # Create profile and experiences first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        create_exp_response = await live_client.post(
            f"/api/v1/profiles/{profile_id}/experiences",
            json=experiences_data,
            headers=headers
        )
        assert create_exp_response.status_code == 201
        created_experiences = create_exp_response.json()

        # Delete experiences
        experience_ids = [exp["id"] for exp in created_experiences]
        response = await live_client.request(
            "DELETE",
            f"/api/v1/profiles/{profile_id}/experiences",
            json={"experience_ids": experience_ids},
            headers=headers
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_get_experiences_list_success(self, live_client: AsyncClient):
        """Test successful retrieval of experiences list."""
        user_data = self._generate_unique_user_data("list_exp")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()
        experiences_data = self._get_sample_experiences()

        # Create profile and experiences first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        create_exp_response = await live_client.post(
            f"/api/v1/profiles/{profile_id}/experiences",
            json=experiences_data,
            headers=headers
        )
        assert create_exp_response.status_code == 201

        # Get experiences list
        response = await live_client.get(
            f"/api/v1/profiles/{profile_id}/experiences",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "experiences" in data
        assert "pagination" in data
        assert len(data["experiences"]) == 2

        # Check pagination
        assert data["pagination"]["total"] == 2
        assert data["pagination"]["limit"] == 50  # Default limit
        assert data["pagination"]["offset"] == 0

    @pytest.mark.asyncio
    async def test_bulk_create_education_success(self, live_client: AsyncClient):
        """Test successful bulk creation of education entries."""
        user_data = self._generate_unique_user_data("bulk_edu")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()
        education_data = self._get_sample_education()

        # Create profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Bulk create education
        response = await live_client.post(
            f"/api/v1/profiles/{profile_id}/education",
            json=education_data,
            headers=headers
        )

        assert response.status_code == 201
        data = response.json()

        # Check response structure
        assert isinstance(data, list)
        assert len(data) == 2

        # Check first education entry
        edu1 = data[0]
        assert "id" in edu1
        assert edu1["institution"] == "University of Washington"
        assert edu1["degree"] == "Bachelor of Science"
        assert edu1["gpa"] == 3.8
        assert len(edu1["honors"]) == 2

        # Check second education entry
        edu2 = data[1]
        assert "id" in edu2
        assert edu2["institution"] == "Stanford University"
        assert edu2["degree"] == "Master of Science"
        assert edu2["gpa"] == 3.9

    @pytest.mark.asyncio
    async def test_bulk_create_projects_success(self, live_client: AsyncClient):
        """Test successful bulk creation of portfolio projects."""
        user_data = self._generate_unique_user_data("bulk_proj")
        headers = await self._get_auth_headers(live_client, user_data)
        profile_data = self._get_sample_profile_data()
        projects_data = self._get_sample_projects()

        # Create profile first
        create_response = await live_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201
        profile_id = create_response.json()["id"]

        # Bulk create projects
        response = await live_client.post(
            f"/api/v1/profiles/{profile_id}/projects",
            json=projects_data,
            headers=headers
        )

        assert response.status_code == 201
        data = response.json()

        # Check response structure
        assert isinstance(data, list)
        assert len(data) == 3

        # Check first project
        proj1 = data[0]
        assert "id" in proj1
        assert proj1["name"] == "E-commerce Platform"
        assert len(proj1["technologies"]) == 4
        assert proj1["url"] == "https://github.com/johndoe/ecommerce"

        # Check second project
        proj2 = data[1]
        assert "id" in proj2
        assert proj2["name"] == "AI Chat Application"
        assert len(proj2["technologies"]) == 4

        # Check third project
        proj3 = data[2]
        assert "id" in proj3
        assert proj3["name"] == "Mobile Fitness Tracker"
        assert len(proj3["technologies"]) == 3