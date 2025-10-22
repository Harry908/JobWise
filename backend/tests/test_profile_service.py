"""Unit tests for ProfileService."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.application.services.profile_service import ProfileService
from app.core.exceptions import ValidationException, NotFoundError, ForbiddenException
from app.domain.entities.profile import Profile, PersonalInfo, Skills, Experience, Education, Project


class TestProfileService:
    """Test cases for ProfileService."""

    @pytest.fixture
    def mock_repository(self):
        """Mock profile repository."""
        return AsyncMock()

    @pytest.fixture
    def profile_service(self, mock_repository):
        """Profile service instance."""
        return ProfileService(mock_repository)

    @pytest.fixture
    def sample_personal_info(self):
        """Sample personal info data."""
        return {
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone": "+1-555-123-4567",
            "location": "Seattle, WA",
            "linkedin": "https://linkedin.com/in/johndoe",
            "github": "https://github.com/johndoe",
            "website": "https://johndoe.com"
        }

    @pytest.fixture
    def sample_skills(self):
        """Sample skills data."""
        return {
            "technical": ["Python", "FastAPI", "React"],
            "soft": ["Leadership", "Communication"],
            "languages": [{"name": "English", "proficiency": "native"}],
            "certifications": [{
                "name": "AWS Solutions Architect",
                "issuer": "Amazon",
                "date_obtained": "2023-01-01",
                "credential_id": "AWS-123"
            }]
        }

    @pytest.fixture
    def sample_profile(self, sample_personal_info, sample_skills):
        """Sample profile entity."""
        return Profile(
            id="profile-123",
            user_id=1,
            personal_info=PersonalInfo(**sample_personal_info),
            professional_summary="Experienced developer",
            skills=Skills(**sample_skills),
            experiences=[],
            education=[],
            projects=[]
        )

    @pytest.mark.asyncio
    async def test_create_profile_success(self, profile_service, mock_repository, sample_personal_info, sample_skills):
        """Test successful profile creation."""
        # Setup
        user_id = 1
        mock_repository.get_by_user_id.return_value = []
        mock_repository.create.return_value = MagicMock()

        # Execute
        result = await profile_service.create_profile(
            user_id=user_id,
            personal_info=sample_personal_info,
            professional_summary="Test summary",
            skills=sample_skills
        )

        # Assert
        mock_repository.get_by_user_id.assert_called_once_with(user_id)
        mock_repository.create.assert_called_once()
        assert result is not None

    @pytest.mark.asyncio
    async def test_create_profile_user_already_has_profile(self, profile_service, mock_repository, sample_personal_info):
        """Test profile creation fails when user already has a profile."""
        # Setup
        user_id = 1
        mock_repository.get_by_user_id.return_value = [MagicMock()]

        # Execute & Assert
        with pytest.raises(ValidationException) as exc_info:
            await profile_service.create_profile(
                user_id=user_id,
                personal_info=sample_personal_info
            )

        assert "already has a profile" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_profile_invalid_personal_info(self, profile_service, mock_repository):
        """Test profile creation fails with invalid personal info."""
        # Setup
        user_id = 1
        invalid_personal_info = {"full_name": "", "email": "invalid-email"}
        mock_repository.get_by_user_id.return_value = []

        # Execute & Assert
        with pytest.raises(ValidationException) as exc_info:
            await profile_service.create_profile(
                user_id=user_id,
                personal_info=invalid_personal_info
            )

        assert "Invalid profile data" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_profile_success(self, profile_service, mock_repository, sample_profile):
        """Test successful profile retrieval."""
        # Setup
        profile_id = "profile-123"
        user_id = 1
        mock_repository.get_by_id.return_value = sample_profile

        # Execute
        result = await profile_service.get_profile(profile_id, user_id)

        # Assert
        mock_repository.get_by_id.assert_called_once_with(profile_id)
        assert result == sample_profile

    @pytest.mark.asyncio
    async def test_get_profile_not_found(self, profile_service, mock_repository):
        """Test profile retrieval fails when profile doesn't exist."""
        # Setup
        profile_id = "profile-123"
        user_id = 1
        mock_repository.get_by_id.return_value = None

        # Execute & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await profile_service.get_profile(profile_id, user_id)

        assert "Profile not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_profile_wrong_owner(self, profile_service, mock_repository, sample_profile):
        """Test profile retrieval fails when accessing another user's profile."""
        # Setup
        profile_id = "profile-123"
        user_id = 1
        sample_profile.user_id = 2  # Different owner
        mock_repository.get_by_id.return_value = sample_profile

        # Execute & Assert
        with pytest.raises(ForbiddenException) as exc_info:
            await profile_service.get_profile(profile_id, user_id)

        assert "Access denied" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user_profiles_success(self, profile_service, mock_repository, sample_profile):
        """Test successful retrieval of user profiles."""
        # Setup
        user_id = 1
        mock_repository.get_by_user_id.return_value = [sample_profile]

        # Execute
        result = await profile_service.get_user_profiles(user_id, limit=10, offset=0)

        # Assert
        mock_repository.get_by_user_id.assert_called_once_with(user_id, 10, 0)
        assert result == [sample_profile]

    @pytest.mark.asyncio
    async def test_get_user_profiles_invalid_limit(self, profile_service, mock_repository):
        """Test user profiles retrieval fails with invalid limit."""
        # Setup
        user_id = 1

        # Execute & Assert
        with pytest.raises(ValidationException) as exc_info:
            await profile_service.get_user_profiles(user_id, limit=0)

        assert "Limit must be between 1 and 100" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user_profiles_invalid_offset(self, profile_service, mock_repository):
        """Test user profiles retrieval fails with invalid offset."""
        # Setup
        user_id = 1

        # Execute & Assert
        with pytest.raises(ValidationException) as exc_info:
            await profile_service.get_user_profiles(user_id, offset=-1)

        assert "Offset must be non-negative" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_active_profile_success(self, profile_service, mock_repository, sample_profile):
        """Test successful retrieval of active profile."""
        # Setup
        user_id = 1
        mock_repository.get_by_user_id.return_value = [sample_profile]

        # Execute
        result = await profile_service.get_active_profile(user_id)

        # Assert
        mock_repository.get_by_user_id.assert_called_once_with(1, 1, 0)
        assert result == sample_profile

    @pytest.mark.asyncio
    async def test_get_active_profile_not_found(self, profile_service, mock_repository):
        """Test active profile retrieval returns None when no profile exists."""
        # Setup
        user_id = 1
        mock_repository.get_by_user_id.return_value = []

        # Execute
        result = await profile_service.get_active_profile(user_id)

        # Assert
        mock_repository.get_by_user_id.assert_called_once_with(1, 1, 0)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_profile_success(self, profile_service, mock_repository, sample_profile):
        """Test successful profile update."""
        # Setup
        profile_id = "profile-123"
        user_id = 1
        mock_repository.get_by_id.return_value = sample_profile
        mock_repository.update.return_value = sample_profile

        # Execute
        result = await profile_service.update_profile(
            profile_id=profile_id,
            user_id=user_id,
            professional_summary="Updated summary"
        )

        # Assert
        mock_repository.get_by_id.assert_called_once_with(profile_id)
        mock_repository.update.assert_called_once()
        assert result is not None

    @pytest.mark.asyncio
    async def test_update_profile_invalid_data(self, profile_service, mock_repository, sample_profile):
        """Test profile update fails with invalid data."""
        # Setup
        profile_id = "profile-123"
        user_id = 1
        mock_repository.get_by_id.return_value = sample_profile

        # Execute & Assert
        with pytest.raises(ValidationException) as exc_info:
            await profile_service.update_profile(
                profile_id=profile_id,
                user_id=user_id,
                personal_info={"full_name": "", "email": "invalid"}
            )

        assert "Invalid personal info" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_profile_success(self, profile_service, mock_repository, sample_profile):
        """Test successful profile deletion."""
        # Setup
        profile_id = "profile-123"
        user_id = 1
        mock_repository.get_by_id.return_value = sample_profile
        mock_repository.delete.return_value = True

        # Execute
        await profile_service.delete_profile(profile_id, user_id)

        # Assert
        mock_repository.get_by_id.assert_called_once_with(profile_id)
        mock_repository.delete.assert_called_once_with(profile_id)

    @pytest.mark.asyncio
    async def test_delete_profile_not_found(self, profile_service, mock_repository):
        """Test profile deletion fails when profile doesn't exist."""
        # Setup
        profile_id = "profile-123"
        user_id = 1
        mock_repository.get_by_id.return_value = None

        # Execute & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await profile_service.delete_profile(profile_id, user_id)

        assert "Profile not found" in str(exc_info.value)

    def test_calculate_completeness_full_profile(self, profile_service, sample_profile):
        """Test completeness calculation for full profile."""
        # Setup - make profile complete
        sample_profile.professional_summary = "Detailed professional summary with enough content to exceed the fifty character minimum requirement for validation"
        sample_profile.experiences = [Experience(
            title="Senior Developer",
            company="Tech Corp",
            location="Seattle, WA",
            start_date="2020-01-01",
            end_date="2023-01-01",
            is_current=False,
            description="Great work"
        )]
        sample_profile.education = [Education(
            institution="University",
            degree="BS",
            field_of_study="CS",
            start_date="2016-01-01",
            end_date="2020-01-01",
            gpa=3.8
        )]
        sample_profile.projects = [Project(
            name="Project",
            description="Description",
            technologies=[],
            url=None,
            start_date="2020-01-01",
            end_date=None
        )]

        # Execute
        result = profile_service._calculate_completeness(sample_profile)

        # Assert
        assert result["overall"] >= 60  # Should be reasonably complete
        assert result["personal_info"] == 100
        assert result["professional_summary"] == 100
        assert result["experiences"] > 0
        assert result["education"] == 50  # 1 education entry = 50 points
        assert result["skills"] == 100
        assert result["projects"] > 0

    def test_calculate_completeness_empty_profile(self, profile_service):
        """Test completeness calculation for empty profile."""
        # Setup
        empty_profile = Profile(
            user_id=1,
            personal_info=PersonalInfo(
                full_name="John",
                email="john@test.com",
                phone=None,
                location=None,
                linkedin=None,
                github=None,
                website=None
            ),
            professional_summary=None,
            skills=Skills()
        )

        # Execute
        result = profile_service._calculate_completeness(empty_profile)

        # Assert
        assert result["overall"] < 50  # Should be incomplete
        assert result["personal_info"] < 100  # Missing phone/location
        assert result["professional_summary"] == 0
        assert result["experiences"] == 0
        assert result["education"] == 0

    def test_calculate_statistics(self, profile_service, sample_profile):
        """Test statistics calculation."""
        # Setup
        sample_profile.experiences = [
            Experience(
                title="Developer",
                company="Company A",
                location="Seattle, WA",
                start_date="2020-01-01",
                end_date="2022-01-01",
                is_current=False,
                description="Work"
            ),
            Experience(
                title="Senior Developer",
                company="Company B",
                location="Seattle, WA",
                start_date="2022-01-01",
                end_date=None,
                is_current=True,
                description="Current work"
            )
        ]
        sample_profile.education = [Education(
            institution="University",
            degree="BS",
            field_of_study="CS",
            start_date="2016-01-01",
            end_date="2020-01-01",
            gpa=3.8
        )]
        sample_profile.skills.technical = ["Python", "Java"]
        sample_profile.skills.soft = ["Leadership"]
        sample_profile.projects = [Project(
            name="Project A",
            description="Description",
            technologies=[],
            url=None,
            start_date="2020-01-01",
            end_date=None
        )]

        # Execute
        result = profile_service._calculate_statistics(sample_profile)

        # Assert
        assert result["total_experiences"] == 2
        assert result["total_education"] == 1
        assert result["total_skills"] == 3  # 2 technical + 1 soft
        assert result["total_projects"] == 1
        assert result["years_of_experience"] >= 2  # At least 2 years from first job

    def test_generate_recommendations(self, profile_service):
        """Test recommendations generation."""
        # Setup - incomplete profile
        incomplete_profile = Profile(
            user_id=1,
            personal_info=PersonalInfo(
                full_name="John",
                email="john@test.com",
                phone=None,
                location=None,
                linkedin=None,
                github=None,
                website=None
            ),
            professional_summary=None,
            skills=Skills()
        )

        completeness = {"personal_info": 50, "professional_summary": 0,
                       "experiences": 0, "education": 0, "skills": 0, "projects": 0}

        # Execute
        result = profile_service._generate_recommendations(incomplete_profile, completeness)

        # Assert
        assert len(result) > 0
        assert any("personal information" in rec for rec in result)
        assert any("professional summary" in rec for rec in result)
        assert any("work experience" in rec for rec in result)
        assert any("education" in rec for rec in result)
        assert any("skills" in rec for rec in result)