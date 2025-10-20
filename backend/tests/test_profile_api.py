"""Comprehensive Profile API tests including service layer, middleware, and API endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.application.services.profile_service import ProfileService
from app.application.dtos.profile_dtos import (
    CreateProfileDTO,
    UpdateProfileDTO,
    ProfileDTO,
    AddExperienceDTO,
    UpdateExperienceDTO,
    RemoveExperienceDTO,
    ProfileAnalyticsDTO,
)
from app.core.exceptions import ValidationException
from app.domain.entities.profile import MasterProfile
from app.domain.entities.user import User
from app.domain.value_objects import PersonalInfo, Experience, Education, Skills, Project
from app.infrastructure.repositories.profile_repository import ProfileRepository


class TestProfileService:
    """Test cases for ProfileService."""

    @pytest.fixture
    def mock_profile_repo(self):
        """Mock profile repository."""
        return AsyncMock(spec=ProfileRepository)

    @pytest.fixture
    def profile_service(self, mock_profile_repo):
        """Profile service instance with mocked repository."""
        return ProfileService(mock_profile_repo)

    @pytest.mark.asyncio
    async def test_create_profile_success(self, profile_service, mock_profile_repo):
        """Test successful profile creation."""
        # Arrange
        user_id = uuid4()
        personal_info = PersonalInfo(
            full_name="John Doe",
            email="john.doe@example.com",
            phone="+1-555-0123",
            location="Seattle, WA",
            linkedin=None,
            github=None,
            website=None
        )

        mock_profile = MagicMock()
        mock_profile.id = uuid4()
        mock_profile.user_id = user_id
        mock_profile.personal_info = personal_info
        mock_profile.version = 1
        mock_profile.is_active = True
        mock_profile.to_dict.return_value = {
            "id": str(mock_profile.id),
            "user_id": str(user_id),
            "personal_info": personal_info.__dict__,
            "experiences": [],
            "education": [],
            "skills": None,
            "projects": [],
            "version": 1,
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }

        mock_profile_repo.create.return_value = mock_profile
        mock_profile_repo.get_by_user_id.return_value = None  # User doesn't have a profile yet

        # Act
        result = await profile_service.create_profile(
            user_id=user_id,
            personal_info=personal_info
        )

        # Assert
        assert result.id == mock_profile.id
        assert result.user_id == user_id
        assert result.personal_info.full_name == "John Doe"
        assert result.version == 1
        assert result.is_active is True

        mock_profile_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_profile_success(self, profile_service, mock_profile_repo):
        """Test successful user profile retrieval."""
        # Arrange
        user_id = uuid4()
        mock_profile = MagicMock()
        mock_profile.user_id = user_id

        mock_profile_repo.get_by_user_id.return_value = mock_profile

        # Act
        result = await profile_service.get_user_profile(user_id)

        # Assert
        assert result == mock_profile
        mock_profile_repo.get_by_user_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_user_profile_not_found(self, profile_service, mock_profile_repo):
        """Test user profile retrieval when profile doesn't exist."""
        # Arrange
        user_id = uuid4()
        mock_profile_repo.get_by_user_id.return_value = None

        # Act
        result = await profile_service.get_user_profile(user_id)

        # Assert
        assert result is None
        mock_profile_repo.get_by_user_id.assert_called_once_with(user_id)


class TestProfileEndpoints:
    """Test cases for Profile API endpoints with FastAPI TestClient."""

    @pytest.fixture
    def test_client(self):
        """Test client for FastAPI app."""
        from app.main import app
        return TestClient(app)

    def test_create_profile_endpoint_success(self, test_client):
        """Test successful profile creation endpoint."""
        import time
        # Use timestamp to ensure unique email
        timestamp = str(int(time.time() * 1000))

        # First register and login a user
        user_data = {
            "email": f"profiletest-{timestamp}@example.com",
            "password": "SecurePass123",
            "full_name": "Profile Test User"
        }
        test_client.post("/api/v1/auth/register", json=user_data)

        login_data = {
            "email": f"profiletest-{timestamp}@example.com",
            "password": "SecurePass123"
        }
        login_response = test_client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()

        # Create profile data
        profile_data = {
            "personal_info": {
                "full_name": "John Doe",
                "email": f"profiletest-{timestamp}@example.com",
                "phone": "+1-555-0123",
                "location": "Seattle, WA",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "portfolio_url": "https://johndoe.dev"
            },
            "professional_summary": "Experienced software developer with 5+ years...",
            "experiences": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Corp",
                    "start_date": "2020-01-01",
                    "end_date": "2023-12-31",
                    "description": "Developed web applications using Python and React",
                    "technologies": ["Python", "FastAPI", "React", "PostgreSQL"],
                    "location": "Seattle, WA",
                    "is_current": False
                }
            ],
            "education": [
                {
                    "institution": "University of Washington",
                    "degree": "Bachelor of Science",
                    "field_of_study": "Computer Science",
                    "start_date": "2016-09-01",
                    "end_date": "2020-06-01",
                    "gpa": 3.8,
                    "location": "Seattle, WA"
                }
            ],
            "skills": {
                "technical": ["Python", "FastAPI", "React", "PostgreSQL"],
                "soft": ["Communication", "Leadership", "Problem Solving"],
                "languages": [
                    {"name": "English", "proficiency": "native"},
                    {"name": "Spanish", "proficiency": "intermediate"}
                ],
                "certifications": [
                    {
                        "name": "AWS Solutions Architect",
                        "issuer": "Amazon Web Services",
                        "date_obtained": "2023-01-15",
                        "credential_id": "AWS-123456",
                        "verification_url": "https://aws.amazon.com/verification"
                    }
                ]
            },
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "description": "Built a full-stack e-commerce platform",
                    "start_date": "2022-01-01",
                    "end_date": "2022-06-01",
                    "technologies": ["Python", "FastAPI", "React", "PostgreSQL"],
                    "repository_url": "https://github.com/johndoe/ecommerce",
                    "demo_url": "https://ecommerce-demo.herokuapp.com"
                }
            ]
        }

        # Act
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = test_client.post("/api/v1/profiles", json=profile_data, headers=headers)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["personal_info"]["full_name"] == "John Doe"
        assert data["personal_info"]["email"] == f"profiletest-{timestamp}@example.com"
        assert len(data["experiences"]) == 1
        assert len(data["education"]) == 1
        assert len(data["projects"]) == 1
        assert "skills" in data

    def test_get_my_profile_endpoint_success(self, test_client):
        """Test successful get my profile endpoint."""
        import time
        timestamp = str(int(time.time() * 1000))

        # Register and login user
        user_data = {
            "email": f"getprofile-{timestamp}@example.com",
            "password": "SecurePass123",
            "full_name": "Get Profile User"
        }
        test_client.post("/api/v1/auth/register", json=user_data)

        login_data = {
            "email": f"getprofile-{timestamp}@example.com",
            "password": "SecurePass123"
        }
        login_response = test_client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()

        # Create profile first
        profile_data = {
            "personal_info": {
                "full_name": "Jane Doe",
                "email": f"getprofile-{timestamp}@example.com",
                "phone": "+1-555-0456",
                "location": "Portland, OR"
            }
        }
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        create_response = test_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        assert create_response.status_code == 201  # Ensure profile creation succeeds

        # Get profile
        response = test_client.get("/api/v1/profiles/me", headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["personal_info"]["full_name"] == "Jane Doe"
        assert data["personal_info"]["location"] == "Portland, OR"

    def test_get_my_profile_endpoint_not_found(self, test_client):
        """Test get my profile when profile doesn't exist."""
        import time
        timestamp = str(int(time.time() * 1000))

        # Register and login user (no profile created)
        user_data = {
            "email": f"noprofile-{timestamp}@example.com",
            "password": "SecurePass123",
            "full_name": "No Profile User"
        }
        test_client.post("/api/v1/auth/register", json=user_data)

        login_data = {
            "email": f"noprofile-{timestamp}@example.com",
            "password": "SecurePass123"
        }
        login_response = test_client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()

        # Try to get profile
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = test_client.get("/api/v1/profiles/me", headers=headers)

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Profile not found" in data["detail"]

    def test_update_profile_endpoint_success(self, test_client):
        """Test successful profile update endpoint."""
        import time
        timestamp = str(int(time.time() * 1000))

        # Register, login, and create profile
        user_data = {
            "email": f"updateprofile-{timestamp}@example.com",
            "password": "SecurePass123",
            "full_name": "Update Profile User"
        }
        test_client.post("/api/v1/auth/register", json=user_data)

        login_data = {
            "email": f"updateprofile-{timestamp}@example.com",
            "password": "SecurePass123"
        }
        login_response = test_client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()

        # Create initial profile
        profile_data = {
            "personal_info": {
                "full_name": "Initial Name",
                "email": f"updateprofile-{timestamp}@example.com",
                "phone": "+1-555-0000",
                "location": "Initial City, ST"
            }
        }
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        create_response = test_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        
        # Debug: Print response details
        print(f"Create response status: {create_response.status_code}")
        print(f"Create response content: {create_response.text}")
        
        assert create_response.status_code == 201, f"Profile creation failed: {create_response.text}"
        profile_id = create_response.json()["id"]
        print(f"Extracted profile_id: {profile_id}")

        # Update profile
        update_data = {
            "personal_info": {
                "full_name": "Updated Name",
                "email": f"updateprofile-{timestamp}@example.com",
                "phone": "+1-555-1111",
                "location": "Updated City, ST"
            },
            "professional_summary": "Updated professional summary"
        }
        response = test_client.put(f"/api/v1/profiles/{profile_id}", json=update_data, headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["personal_info"]["full_name"] == "Updated Name"
        assert data["personal_info"]["phone"] == "+1-555-1111"
        assert data["professional_summary"] == "Updated professional summary"

    def test_delete_profile_endpoint_success(self, test_client):
        """Test successful profile deletion endpoint."""
        import time
        timestamp = str(int(time.time() * 1000))

        # Register, login, and create profile
        user_data = {
            "email": f"deleteprofile-{timestamp}@example.com",
            "password": "SecurePass123",
            "full_name": "Delete Profile User"
        }
        test_client.post("/api/v1/auth/register", json=user_data)

        login_data = {
            "email": f"deleteprofile-{timestamp}@example.com",
            "password": "SecurePass123"
        }
        login_response = test_client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()

        # Create profile
        profile_data = {
            "personal_info": {
                "full_name": "Delete Me",
                "email": f"deleteprofile-{timestamp}@example.com",
                "phone": "+1-555-9999",
                "location": "Delete City, ST"
            }
        }
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        create_response = test_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        profile_id = create_response.json()["id"]

        # Delete profile
        response = test_client.delete(f"/api/v1/profiles/{profile_id}", headers=headers)

        # Assert
        assert response.status_code == 204

        # Verify profile is gone
        get_response = test_client.get("/api/v1/profiles/me", headers=headers)
        assert get_response.status_code == 404

    def test_add_experience_endpoint_success(self, test_client):
        """Test successful add experience endpoint."""
        import time
        timestamp = str(int(time.time() * 1000))

        # Register, login, and create profile
        user_data = {
            "email": f"addexp-{timestamp}@example.com",
            "password": "SecurePass123",
            "full_name": "Add Experience User"
        }
        test_client.post("/api/v1/auth/register", json=user_data)

        login_data = {
            "email": f"addexp-{timestamp}@example.com",
            "password": "SecurePass123"
        }
        login_response = test_client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()

        # Create profile
        profile_data = {
            "personal_info": {
                "full_name": "Experience Tester",
                "email": f"addexp-{timestamp}@example.com",
                "phone": "+1-555-2222",
                "location": "Experience City, ST"
            }
        }
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        create_response = test_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        profile_id = create_response.json()["id"]

        # Add experience
        experience_data = {
            "experience": {
                "title": "Senior Developer",
                "company": "New Company",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "description": "Led development of new features",
                "technologies": ["Python", "AWS", "Docker"],
                "location": "Remote",
                "is_current": False
            }
        }
        response = test_client.post(f"/api/v1/profiles/{profile_id}/experiences", json=experience_data, headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["experiences"]) == 1
        assert data["experiences"][0]["company"] == "New Company"
        assert data["experiences"][0]["title"] == "Senior Developer"

    def test_get_profile_analytics_endpoint_success(self, test_client):
        """Test successful profile analytics endpoint."""
        import time
        timestamp = str(int(time.time() * 1000))

        # Register, login, and create profile with data
        user_data = {
            "email": f"analytics-{timestamp}@example.com",
            "password": "SecurePass123",
            "full_name": "Analytics User"
        }
        test_client.post("/api/v1/auth/register", json=user_data)

        login_data = {
            "email": f"analytics-{timestamp}@example.com",
            "password": "SecurePass123"
        }
        login_response = test_client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()

        # Create profile with experiences and skills
        profile_data = {
            "personal_info": {
                "full_name": "Analytics Tester",
                "email": f"analytics-{timestamp}@example.com",
                "phone": "+1-555-3333",
                "location": "Analytics City, ST"
            },
            "experiences": [
                {
                    "title": "Developer",
                    "company": "Tech Corp",
                    "start_date": "2020-01-01",
                    "end_date": "2023-01-01",
                    "description": "Developed applications using Python and JavaScript",
                    "technologies": ["Python", "JavaScript", "React"],
                    "location": "Remote",
                    "is_current": False
                }
            ],
            "skills": {
                "technical": ["Python", "JavaScript", "AWS"],
                "soft": ["Communication", "Leadership"],
                "languages": [{"name": "English", "proficiency": "native"}],
                "certifications": []
            }
        }
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        create_response = test_client.post("/api/v1/profiles", json=profile_data, headers=headers)
        profile_id = create_response.json()["id"]

        # Get analytics
        response = test_client.get(f"/api/v1/profiles/{profile_id}/analytics", headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "total_experiences" in data
        assert "technical_skills_count" in data
        assert "years_experience" in data
        assert data["total_experiences"] == 1
        assert data["technical_skills_count"] == 3  # Python, JavaScript, AWS

    def test_unauthorized_access_to_other_profile(self, test_client):
        """Test that users cannot access other users' profiles."""
        import time
        timestamp = str(int(time.time() * 1000))

        # Create two users
        user1_data = {
            "email": f"user1-{timestamp}@example.com",
            "password": "SecurePass123",
            "full_name": "User One"
        }
        user2_data = {
            "email": f"user2-{timestamp}@example.com",
            "password": "SecurePass123",
            "full_name": "User Two"
        }
        test_client.post("/api/v1/auth/register", json=user1_data)
        test_client.post("/api/v1/auth/register", json=user2_data)

        # Login as user 1 and create profile
        login1_data = {
            "email": f"user1-{timestamp}@example.com",
            "password": "SecurePass123"
        }
        login1_response = test_client.post("/api/v1/auth/login", json=login1_data)
        tokens1 = login1_response.json()

        profile_data = {
            "personal_info": {
                "full_name": "User One Profile",
                "email": f"user1-{timestamp}@example.com",
                "phone": "+1-555-4444",
                "location": "User1 City, ST"
            }
        }
        headers1 = {"Authorization": f"Bearer {tokens1['access_token']}"}
        create_response = test_client.post("/api/v1/profiles", json=profile_data, headers=headers1)
        profile_id = create_response.json()["id"]

        # Login as user 2 and try to access user 1's profile
        login2_data = {
            "email": f"user2-{timestamp}@example.com",
            "password": "SecurePass123"
        }
        login2_response = test_client.post("/api/v1/auth/login", json=login2_data)
        tokens2 = login2_response.json()

        headers2 = {"Authorization": f"Bearer {tokens2['access_token']}"}
        response = test_client.get(f"/api/v1/profiles/{profile_id}", headers=headers2)

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "Access denied" in data["detail"]


class TestProfileAPIIntegration:
    """Integration tests for Profile API endpoints."""

    @pytest.mark.asyncio
    async def test_profile_api_end_to_end(self):
        """Test complete profile management flow."""
        import httpx
        import time

        timestamp = str(int(time.time()))
        email = f'integration-profile-{timestamp}@example.com'

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Register user
            register_data = {
                'email': email,
                'password': 'SecurePass123',
                'full_name': 'Profile Integration Test User'
            }
            register_response = await client.post('/api/v1/auth/register', json=register_data)
            assert register_response.status_code == 201

            # Login
            login_data = {'email': email, 'password': 'SecurePass123'}
            login_response = await client.post('/api/v1/auth/login', json=login_data)
            assert login_response.status_code == 200
            tokens = login_response.json()

            headers = {'Authorization': f'Bearer {tokens["access_token"]}'}

            # Create profile
            profile_data = {
                'personal_info': {
                    'full_name': 'Integration Test User',
                    'email': email,
                    'phone': '+1-555-0199',
                    'location': 'Integration City, ST'
                },
                'professional_summary': 'Experienced developer in test automation',
                'experiences': [{
                    'title': 'QA Engineer',
                    'company': 'Test Corp',
                    'start_date': '2022-01-01',
                    'end_date': '2023-01-01',
                    'description': 'Automated testing with Python and Selenium',
                    'achievements': ['Implemented automated test suites', 'Reduced manual testing time by 50%'],
                    'location': 'Remote',
                    'is_current': False
                }],
                'skills': {
                    'technical': ['Python', 'Selenium', 'pytest'],
                    'soft': ['Problem Solving'],
                    'languages': [{'name': 'English', 'proficiency': 'fluent'}],
                    'certifications': []
                }
            }
            create_response = await client.post('/api/v1/profiles', json=profile_data, headers=headers)
            assert create_response.status_code == 201
            profile = create_response.json()
            profile_id = profile['id']

            # Get profile
            get_response = await client.get('/api/v1/profiles/me', headers=headers)
            assert get_response.status_code == 200
            retrieved_profile = get_response.json()
            assert retrieved_profile['personal_info']['full_name'] == 'Integration Test User'
            assert len(retrieved_profile['experiences']) == 1

            # Update profile
            update_data = {
                'personal_info': {
                    'full_name': 'Updated Integration Test User',
                    'email': email,
                    'phone': '+1-555-0199',
                    'location': 'Updated City, ST'
                }
            }
            update_response = await client.put(f'/api/v1/profiles/{profile_id}', json=update_data, headers=headers)
            assert update_response.status_code == 200
            updated_profile = update_response.json()
            assert updated_profile['personal_info']['full_name'] == 'Updated Integration Test User'
            assert updated_profile['personal_info']['location'] == 'Updated City, ST'

            # Get analytics
            analytics_response = await client.get(f'/api/v1/profiles/{profile_id}/analytics', headers=headers)
            assert analytics_response.status_code == 200
            analytics = analytics_response.json()
            assert analytics['total_experiences'] == 1
            assert analytics['technical_skills_count'] == 3

            # Add another experience
            experience_data = {
                'experience': {
                    'title': 'Senior QA Engineer',
                    'company': 'New Corp',
                    'start_date': '2023-02-01',
                    'end_date': None,
                    'description': 'Leading QA automation efforts',
                    'achievements': ['Built CI/CD pipelines for automated testing', 'Mentored junior QA engineers'],
                    'location': 'Remote',
                    'is_current': True
                }
            }
            add_exp_response = await client.post(f'/api/v1/profiles/{profile_id}/experiences', json=experience_data, headers=headers)
            assert add_exp_response.status_code == 200
            profile_with_exp = add_exp_response.json()
            assert len(profile_with_exp['experiences']) == 2

            # Delete profile
            delete_response = await client.delete(f'/api/v1/profiles/{profile_id}', headers=headers)
            assert delete_response.status_code == 204

            # Verify profile is gone
            get_deleted_response = await client.get('/api/v1/profiles/me', headers=headers)
            assert get_deleted_response.status_code == 404

            # End of async with block
    # End of test method
# End of TestProfileAPIIntegration class
