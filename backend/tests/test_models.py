"""Database models tests."""

import pytest
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.models import (
    Base,
    UserModel,
    MasterProfileModel,
    ExperienceModel,
    EducationModel,
    SkillModel,
    LanguageModel,
    CertificationModel,
    ProjectModel,
    JobPostingModel,
    GenerationModel,
    GenerationResultModel,
    JobApplicationModel,
    UserSessionModel,
    AuditLogModel
)
from app.domain.value_objects import ProficiencyLevel, SkillCategory
from app.domain.entities.job import JobType, ExperienceLevel
from app.domain.entities.generation import GenerationStatus, DocumentType


class TestUserModel:
    """Test User model functionality."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session):
        """Test creating a user."""
        user = UserModel(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.generations_this_month == 0

    @pytest.mark.asyncio
    async def test_user_unique_email_constraint(self, db_session: AsyncSession):
        """Test unique email constraint."""
        # Create first user
        user1 = UserModel(
            email="unique@example.com",
            password_hash="hash1"
        )
        db_session.add(user1)
        await db_session.commit()

        # Try to create second user with same email
        user2 = UserModel(
            email="unique@example.com",
            password_hash="hash2"
        )
        db_session.add(user2)

        with pytest.raises(Exception):  # IntegrityError
            await db_session.commit()


class TestMasterProfileModel:
    """Test Master Profile model functionality."""

    @pytest.mark.asyncio
    async def test_create_profile(self, db_session: AsyncSession):
        """Test creating a master profile."""
        # First create a user
        user = UserModel(
            email="profile_test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        await db_session.commit()

        # Create profile
        profile = MasterProfileModel(
            user_id=user.id,
            full_name="John Doe",
            email="john.doe@example.com",
            professional_summary="Experienced developer"
        )
        db_session.add(profile)
        await db_session.commit()
        await db_session.refresh(profile)

        assert profile.id is not None
        assert profile.user_id == user.id
        assert profile.version == 1
        assert profile.is_active is True

    @pytest.mark.asyncio
    async def test_profile_user_relationship(self, db_session: AsyncSession):
        """Test profile-user relationship."""
        user = UserModel(
            email="relation_test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        await db_session.commit()

        profile = MasterProfileModel(
            user_id=user.id,
            full_name="Jane Smith",
            email="jane.smith@example.com"
        )
        db_session.add(profile)
        await db_session.commit()

        # Test relationship loading
        await db_session.refresh(profile, ['user'])
        assert profile.user.email == "relation_test@example.com"


class TestExperienceModel:
    """Test Experience model functionality."""

    @pytest.mark.asyncio
    async def test_create_experience(self, db_session: AsyncSession):
        """Test creating work experience."""
        # Create user and profile first
        user = UserModel(email="exp_test@example.com", password_hash="hash")
        db_session.add(user)
        await db_session.commit()

        profile = MasterProfileModel(
            user_id=user.id,
            full_name="Test User",
            email="test@example.com"
        )
        db_session.add(profile)
        await db_session.commit()

        # Create experience
        experience = ExperienceModel(
            profile_id=profile.id,
            title="Software Engineer",
            company="Tech Corp",
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),
            description="Developed software applications",
            achievements=["Achievement 1", "Achievement 2"]
        )
        db_session.add(experience)
        await db_session.commit()
        await db_session.refresh(experience)

        assert experience.id is not None
        assert experience.is_current is False
        assert experience.display_order == 0

    @pytest.mark.asyncio
    async def test_experience_date_validation(self, db_session: AsyncSession):
        """Test experience date validation constraints."""
        user = UserModel(email="date_test@example.com", password_hash="hash")
        db_session.add(user)
        await db_session.commit()

        profile = MasterProfileModel(
            user_id=user.id,
            full_name="Test User",
            email="test@example.com"
        )
        db_session.add(profile)
        await db_session.commit()

        # Test invalid dates (end before start)
        experience = ExperienceModel(
            profile_id=profile.id,
            title="Test",
            company="Test Corp",
            start_date=date(2023, 1, 1),
            end_date=date(2020, 1, 1),  # End before start
            description="Test"
        )
        db_session.add(experience)

        with pytest.raises(Exception):  # Check constraint violation
            await db_session.commit()


class TestSkillModel:
    """Test Skill model functionality."""

    @pytest.mark.asyncio
    async def test_create_skill(self, db_session: AsyncSession):
        """Test creating a skill."""
        # Create user and profile
        user = UserModel(email="skill_test@example.com", password_hash="hash")
        db_session.add(user)
        await db_session.commit()

        profile = MasterProfileModel(
            user_id=user.id,
            full_name="Test User",
            email="test@example.com"
        )
        db_session.add(profile)
        await db_session.commit()

        # Create skill
        skill = SkillModel(
            profile_id=profile.id,
            name="Python",
            category=SkillCategory.TECHNICAL,
            proficiency_level=ProficiencyLevel.ADVANCED,
            years_experience=3.5
        )
        db_session.add(skill)
        await db_session.commit()
        await db_session.refresh(skill)

        assert skill.id is not None
        assert skill.category == SkillCategory.TECHNICAL
        assert skill.proficiency_level == ProficiencyLevel.ADVANCED
        assert skill.years_experience == 3.5

    @pytest.mark.asyncio
    async def test_skill_unique_constraint(self, db_session: AsyncSession):
        """Test skill uniqueness constraint."""
        user = UserModel(email="unique_skill_test@example.com", password_hash="hash")
        db_session.add(user)
        await db_session.commit()

        profile = MasterProfileModel(
            user_id=user.id,
            full_name="Test User",
            email="test@example.com"
        )
        db_session.add(profile)
        await db_session.commit()

        # Create first skill
        skill1 = SkillModel(
            profile_id=profile.id,
            name="Python",
            category=SkillCategory.TECHNICAL
        )
        db_session.add(skill1)
        await db_session.commit()

        # Try to create duplicate skill
        skill2 = SkillModel(
            profile_id=profile.id,
            name="Python",
            category=SkillCategory.TECHNICAL
        )
        db_session.add(skill2)

        with pytest.raises(Exception):  # Unique constraint violation
            await db_session.commit()


class TestJobPostingModel:
    """Test Job Posting model functionality."""

    @pytest.mark.asyncio
    async def test_create_job_posting(self, db_session: AsyncSession):
        """Test creating a job posting."""
        job = JobPostingModel(
            id="job_123",
            title="Senior Python Developer",
            company="Tech Corp",
            location="Seattle, WA",
            description="We are looking for a senior Python developer...",
            requirements=["Python", "FastAPI", "PostgreSQL"],
            job_type=JobType.FULL_TIME,
            experience_level=ExperienceLevel.SENIOR,
            posted_date=datetime.utcnow(),
            source="indeed"
        )
        db_session.add(job)
        await db_session.commit()
        await db_session.refresh(job)

        assert job.id == "job_123"
        assert job.remote is False  # Default value
        assert job.salary_currency == "USD"  # Default value

    @pytest.mark.asyncio
    async def test_job_salary_constraints(self, db_session: AsyncSession):
        """Test job salary constraint validation."""
        job = JobPostingModel(
            id="salary_test",
            title="Test Job",
            company="Test Corp",
            location="Test City",
            description="Test description",
            requirements=["Test"],
            job_type=JobType.FULL_TIME,
            experience_level=ExperienceLevel.MID,
            posted_date=datetime.utcnow(),
            source="test",
            salary_min=50000,
            salary_max=30000  # Max < Min - should fail
        )
        db_session.add(job)

        with pytest.raises(Exception):  # Check constraint violation
            await db_session.commit()


class TestGenerationModel:
    """Test Generation model functionality."""

    @pytest.mark.asyncio
    async def test_create_generation(self, db_session: AsyncSession):
        """Test creating a generation record."""
        # Create user, profile, and job first
        user = UserModel(email="gen_test@example.com", password_hash="hash")
        db_session.add(user)
        await db_session.commit()

        profile = MasterProfileModel(
            user_id=user.id,
            full_name="Test User",
            email="test@example.com"
        )
        db_session.add(profile)
        await db_session.commit()

        job = JobPostingModel(
            id="gen_job_123",
            title="Test Job",
            company="Test Corp",
            location="Test City",
            description="Test",
            requirements=["Test"],
            job_type=JobType.FULL_TIME,
            experience_level=ExperienceLevel.MID,
            posted_date=datetime.utcnow(),
            source="test"
        )
        db_session.add(job)
        await db_session.commit()

        # Create generation
        generation = GenerationModel(
            user_id=user.id,
            profile_id=profile.id,
            job_id=job.id,
            status=GenerationStatus.PENDING
        )
        db_session.add(generation)
        await db_session.commit()
        await db_session.refresh(generation)

        assert generation.id is not None
        assert generation.status == GenerationStatus.PENDING
        assert generation.retry_count == 0


class TestAuditLogModel:
    """Test Audit Log model functionality."""

    @pytest.mark.asyncio
    async def test_create_audit_log(self, db_session: AsyncSession):
        """Test creating an audit log entry."""
        audit_log = AuditLogModel(
            event_type="user_login",
            event_description="User logged in successfully",
            severity="info",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0..."
        )
        db_session.add(audit_log)
        await db_session.commit()
        await db_session.refresh(audit_log)

        assert audit_log.id is not None
        assert audit_log.event_type == "user_login"
        assert audit_log.severity == "info"


class TestModelRelationships:
    """Test model relationships and foreign keys."""

    @pytest.mark.asyncio
    async def test_cascade_delete_user(self, db_session: AsyncSession):
        """Test cascade delete from user to related models."""
        # Create user
        user = UserModel(email="cascade_test@example.com", password_hash="hash")
        db_session.add(user)
        await db_session.commit()

        # Create profile
        profile = MasterProfileModel(
            user_id=user.id,
            full_name="Test User",
            email="test@example.com"
        )
        db_session.add(profile)
        await db_session.commit()

        # Create experience
        experience = ExperienceModel(
            profile_id=profile.id,
            title="Test",
            company="Test Corp",
            start_date=date(2020, 1, 1),
            description="Test"
        )
        db_session.add(experience)
        await db_session.commit()

        # Delete user - should cascade to profile and experience
        await db_session.delete(user)
        await db_session.commit()

        # Verify cascade worked
        from sqlalchemy import text
        profile_count = await db_session.execute(
            text("SELECT COUNT(*) FROM master_profiles WHERE user_id = :user_id"),
            {"user_id": user.id}
        )
        assert profile_count.scalar() == 0

        experience_count = await db_session.execute(
            text("SELECT COUNT(*) FROM experiences WHERE profile_id = :profile_id"),
            {"profile_id": profile.id}
        )
        assert experience_count.scalar() == 0