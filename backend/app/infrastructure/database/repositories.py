"""Database repository implementations for SQLAlchemy models."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid

from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import IntegrityError

from .models import (
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
from ...domain.entities.profile import MasterProfile
from ...domain.entities.job import JobPosting
from ...domain.entities.generation import Generation
from ...core.exceptions import (
    EntityNotFoundError,
    DuplicateEntityError,
    DatabaseError
)
from ...core.logging import get_logger

logger = get_logger(__name__)


class BaseRepository(ABC):
    """Base repository class with common CRUD operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def commit(self) -> None:
        """Commit transaction."""
        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to commit transaction: {e}")
            raise DatabaseError(f"Transaction failed: {str(e)}")
    
    async def rollback(self) -> None:
        """Rollback transaction."""
        await self.session.rollback()


class UserRepository(BaseRepository):
    """User repository for database operations."""
    
    async def create(self, user_data: dict) -> UserModel:
        """Create a new user."""
        try:
            user = UserModel(
                id=str(uuid.uuid4()),
                **user_data
            )
            self.session.add(user)
            await self.commit()
            return user
        except IntegrityError as e:
            await self.rollback()
            if "email" in str(e):
                raise DuplicateEntityError("User with this email already exists")
            raise DatabaseError(f"Failed to create user: {str(e)}")
    
    async def get_by_id(self, user_id: str) -> Optional[UserModel]:
        """Get user by ID."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none()
    
    async def update(self, user_id: str, update_data: dict) -> UserModel:
        """Update user."""
        user = await self.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found")
        
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        await self.commit()
        return user
    
    async def delete(self, user_id: str) -> bool:
        """Delete user."""
        result = await self.session.execute(
            delete(UserModel).where(UserModel.id == user_id)
        )
        await self.commit()
        return result.rowcount > 0
    
    async def increment_generations_count(self, user_id: str) -> None:
        """Increment user's generations count for the month."""
        await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(
                generations_this_month=UserModel.generations_this_month + 1,
                last_active_at=func.now(),
                updated_at=func.now()
            )
        )
        await self.commit()
    
    async def reset_monthly_generations(self, user_ids: List[str]) -> None:
        """Reset monthly generations count for users."""
        await self.session.execute(
            update(UserModel)
            .where(UserModel.id.in_(user_ids))
            .values(
                generations_this_month=0,
                updated_at=func.now()
            )
        )
        await self.commit()
    
    async def update_last_login(self, user_id: str) -> None:
        """Update user's last login timestamp."""
        await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(
                last_active_at=func.now(),
                updated_at=func.now()
            )
        )
        await self.commit()


class MasterProfileRepository(BaseRepository):
    """Master profile repository for database operations."""
    
    async def create(self, profile_data: dict) -> MasterProfileModel:
        """Create a new master profile."""
        try:
            profile = MasterProfileModel(
                id=str(uuid.uuid4()),
                **profile_data
            )
            self.session.add(profile)
            await self.commit()
            return profile
        except IntegrityError as e:
            await self.rollback()
            raise DuplicateEntityError("Profile with this email already exists for user")
    
    async def get_by_id(self, profile_id: str, include_relations: bool = False) -> Optional[MasterProfileModel]:
        """Get profile by ID with optional relations."""
        query = select(MasterProfileModel).where(MasterProfileModel.id == profile_id)
        
        if include_relations:
            query = query.options(
                selectinload(MasterProfileModel.experiences),
                selectinload(MasterProfileModel.education),
                selectinload(MasterProfileModel.skills),
                selectinload(MasterProfileModel.languages),
                selectinload(MasterProfileModel.certifications),
                selectinload(MasterProfileModel.projects)
            )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: str, active_only: bool = True) -> List[MasterProfileModel]:
        """Get profiles by user ID."""
        query = select(MasterProfileModel).where(MasterProfileModel.user_id == user_id)
        
        if active_only:
            query = query.where(MasterProfileModel.is_active == True)
        
        query = query.order_by(MasterProfileModel.updated_at.desc())
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update(self, profile_id: str, update_data: dict) -> MasterProfileModel:
        """Update profile."""
        profile = await self.get_by_id(profile_id)
        if not profile:
            raise EntityNotFoundError(f"Profile with ID {profile_id} not found")
        
        for field, value in update_data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        
        profile.updated_at = datetime.utcnow()
        profile.version += 1
        await self.commit()
        return profile
    
    async def deactivate(self, profile_id: str) -> bool:
        """Deactivate profile."""
        profile = await self.get_by_id(profile_id)
        if not profile:
            return False
        
        profile.is_active = False
        profile.updated_at = datetime.utcnow()
        await self.commit()
        return True


class JobPostingRepository(BaseRepository):
    """Job posting repository for database operations."""
    
    async def create_or_update(self, job_data: dict) -> JobPostingModel:
        """Create new job posting or update existing one."""
        existing_job = await self.get_by_id(job_data['id'])
        
        if existing_job:
            # Update existing job
            for field, value in job_data.items():
                if hasattr(existing_job, field):
                    setattr(existing_job, field, value)
            existing_job.updated_at = datetime.utcnow()
            await self.commit()
            return existing_job
        else:
            # Create new job
            job = JobPostingModel(**job_data)
            self.session.add(job)
            await self.commit()
            return job
    
    async def get_by_id(self, job_id: str) -> Optional[JobPostingModel]:
        """Get job by ID."""
        result = await self.session.execute(
            select(JobPostingModel).where(JobPostingModel.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def search_jobs(
        self, 
        keywords: List[str] = None,
        location: str = None,
        remote: bool = None,
        job_type: str = None,
        experience_level: str = None,
        salary_min: int = None,
        company: str = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[JobPostingModel]:
        """Search jobs with filters."""
        query = select(JobPostingModel)
        
        # Add filters
        conditions = []
        
        if keywords:
            # Simple keyword search in title and description
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.extend([
                    JobPostingModel.title.icontains(keyword),
                    JobPostingModel.description.icontains(keyword)
                ])
            conditions.append(or_(*keyword_conditions))
        
        if location:
            conditions.append(JobPostingModel.location.icontains(location))
        
        if remote is not None:
            conditions.append(JobPostingModel.remote == remote)
        
        if job_type:
            conditions.append(JobPostingModel.job_type == job_type)
        
        if experience_level:
            conditions.append(JobPostingModel.experience_level == experience_level)
        
        if salary_min:
            conditions.append(JobPostingModel.salary_min >= salary_min)
        
        if company:
            conditions.append(JobPostingModel.company.icontains(company))
        
        # Filter out expired jobs
        conditions.append(
            or_(
                JobPostingModel.expires_date.is_(None),
                JobPostingModel.expires_date > func.now()
            )
        )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(JobPostingModel.posted_date.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_recent_jobs(self, days: int = 7, limit: int = 50) -> List[JobPostingModel]:
        """Get recent job postings."""
        cutoff_date = func.now() - func.interval(f'{days} days')
        
        result = await self.session.execute(
            select(JobPostingModel)
            .where(JobPostingModel.posted_date >= cutoff_date)
            .order_by(JobPostingModel.posted_date.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def delete_expired_jobs(self) -> int:
        """Delete expired job postings."""
        result = await self.session.execute(
            delete(JobPostingModel)
            .where(
                and_(
                    JobPostingModel.expires_date.is_not(None),
                    JobPostingModel.expires_date < func.now()
                )
            )
        )
        await self.commit()
        return result.rowcount


class GenerationRepository(BaseRepository):
    """Generation repository for database operations."""
    
    async def create(self, generation_data: dict) -> GenerationModel:
        """Create a new generation."""
        generation = GenerationModel(
            id=str(uuid.uuid4()),
            **generation_data
        )
        self.session.add(generation)
        await self.commit()
        return generation
    
    async def get_by_id(self, generation_id: str, include_results: bool = False) -> Optional[GenerationModel]:
        """Get generation by ID."""
        query = select(GenerationModel).where(GenerationModel.id == generation_id)
        
        if include_results:
            query = query.options(selectinload(GenerationModel.results))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_user_id(
        self, 
        user_id: str, 
        status: str = None, 
        limit: int = 20,
        offset: int = 0
    ) -> List[GenerationModel]:
        """Get generations by user ID."""
        query = select(GenerationModel).where(GenerationModel.user_id == user_id)
        
        if status:
            query = query.where(GenerationModel.status == status)
        
        query = query.order_by(GenerationModel.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update_status(self, generation_id: str, status: str, **kwargs) -> GenerationModel:
        """Update generation status."""
        generation = await self.get_by_id(generation_id)
        if not generation:
            raise EntityNotFoundError(f"Generation with ID {generation_id} not found")
        
        generation.status = status
        generation.updated_at = datetime.utcnow()
        
        # Update additional fields
        for field, value in kwargs.items():
            if hasattr(generation, field):
                setattr(generation, field, value)
        
        await self.commit()
        return generation
    
    async def add_result(self, generation_id: str, result_data: dict) -> GenerationResultModel:
        """Add generation result."""
        result = GenerationResultModel(
            id=str(uuid.uuid4()),
            generation_id=generation_id,
            **result_data
        )
        self.session.add(result)
        await self.commit()
        return result
    
    async def get_user_monthly_count(self, user_id: str) -> int:
        """Get user's generation count for current month."""
        start_of_month = func.date_trunc('month', func.now())
        
        result = await self.session.execute(
            select(func.count(GenerationModel.id))
            .where(
                and_(
                    GenerationModel.user_id == user_id,
                    GenerationModel.created_at >= start_of_month
                )
            )
        )
        return result.scalar() or 0
    
    async def get_pending_generations(self, limit: int = 10) -> List[GenerationModel]:
        """Get pending generations for processing."""
        result = await self.session.execute(
            select(GenerationModel)
            .where(GenerationModel.status == 'pending')
            .order_by(GenerationModel.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()


class JobApplicationRepository(BaseRepository):
    """Job application repository for database operations."""
    
    async def create(self, application_data: dict) -> JobApplicationModel:
        """Create a new job application."""
        try:
            application = JobApplicationModel(
                id=str(uuid.uuid4()),
                **application_data
            )
            self.session.add(application)
            await self.commit()
            return application
        except IntegrityError:
            await self.rollback()
            raise DuplicateEntityError("Application already exists for this job")
    
    async def get_by_user_id(
        self,
        user_id: str,
        status: str = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[JobApplicationModel]:
        """Get applications by user ID."""
        query = (
            select(JobApplicationModel)
            .options(joinedload(JobApplicationModel.job_posting))
            .where(JobApplicationModel.user_id == user_id)
        )
        
        if status:
            query = query.where(JobApplicationModel.status == status)
        
        query = query.order_by(JobApplicationModel.applied_date.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update_status(self, application_id: str, status: str, **kwargs) -> JobApplicationModel:
        """Update application status."""
        result = await self.session.execute(
            select(JobApplicationModel).where(JobApplicationModel.id == application_id)
        )
        application = result.scalar_one_or_none()
        
        if not application:
            raise EntityNotFoundError(f"Application with ID {application_id} not found")
        
        application.status = status
        application.updated_at = datetime.utcnow()
        
        # Update additional fields
        for field, value in kwargs.items():
            if hasattr(application, field):
                setattr(application, field, value)
        
        await self.commit()
        return application
    
    async def get_applications_needing_follow_up(self) -> List[JobApplicationModel]:
        """Get applications that need follow-up."""
        result = await self.session.execute(
            select(JobApplicationModel)
            .options(joinedload(JobApplicationModel.job_posting))
            .where(
                and_(
                    JobApplicationModel.follow_up_date <= func.now(),
                    JobApplicationModel.status.in_(['applied', 'under_review'])
                )
            )
            .order_by(JobApplicationModel.follow_up_date.asc())
        )
        return result.scalars().all()


class AuditLogRepository(BaseRepository):
    """Audit log repository for database operations."""
    
    async def create_log(
        self,
        event_type: str,
        event_description: str,
        user_id: str = None,
        resource_type: str = None,
        resource_id: str = None,
        metadata: dict = None,
        severity: str = "info",
        ip_address: str = None,
        user_agent: str = None
    ) -> AuditLogModel:
        """Create an audit log entry."""
        log_entry = AuditLogModel(
            id=str(uuid.uuid4()),
            event_type=event_type,
            event_description=event_description,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata or {},
            severity=severity,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.session.add(log_entry)
        await self.commit()
        return log_entry
    
    async def get_user_logs(
        self,
        user_id: str,
        event_type: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AuditLogModel]:
        """Get audit logs for a user."""
        query = select(AuditLogModel).where(AuditLogModel.user_id == user_id)
        
        if event_type:
            query = query.where(AuditLogModel.event_type == event_type)
        
        query = query.order_by(AuditLogModel.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_system_logs(
        self,
        severity: str = None,
        event_type: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLogModel]:
        """Get system audit logs."""
        query = select(AuditLogModel)
        
        conditions = []
        if severity:
            conditions.append(AuditLogModel.severity == severity)
        if event_type:
            conditions.append(AuditLogModel.event_type == event_type)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(AuditLogModel.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return result.scalars().all()


# Repository factory for dependency injection
class RepositoryFactory:
    """Factory for creating repository instances."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def create_user_repository(self) -> UserRepository:
        return UserRepository(self.session)
    
    def create_profile_repository(self) -> MasterProfileRepository:
        return MasterProfileRepository(self.session)
    
    def create_job_repository(self) -> JobPostingRepository:
        return JobPostingRepository(self.session)
    
    def create_generation_repository(self) -> GenerationRepository:
        return GenerationRepository(self.session)
    
    def create_application_repository(self) -> JobApplicationRepository:
        return JobApplicationRepository(self.session)
    
    def create_audit_repository(self) -> AuditLogRepository:
        return AuditLogRepository(self.session)