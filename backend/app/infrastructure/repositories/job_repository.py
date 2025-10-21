# Job repository
from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
import json
from datetime import datetime
import uuid

from app.application.dtos.job_dtos import JobDTO, JobFiltersDTO, SalaryRangeDTO


class JobRepositoryInterface(ABC):
    """Abstract interface for job data access"""

    @abstractmethod
    async def get_all_jobs(self) -> List[JobDTO]:
        """Get all jobs"""
        pass

    @abstractmethod
    async def get_job_by_id(self, job_id: str) -> Optional[JobDTO]:
        """Get a specific job by ID"""
        pass

    @abstractmethod
    async def search_jobs(
        self,
        query: str = "",
        filters: Optional[JobFiltersDTO] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[JobDTO]:
        """Search jobs with filters and pagination"""
        pass

    @abstractmethod
    async def get_job_filters(self) -> JobFiltersDTO:
        """Get available filter options"""
        pass

    @abstractmethod
    async def get_filter_options(self) -> dict:
        """Get filter options as dictionary"""
        pass

    @abstractmethod
    async def get_statistics(self) -> dict:
        """Get job statistics"""
        pass

    @abstractmethod
    async def get_total_count(self) -> int:
        """Get total number of jobs"""
        pass


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, func
from ...infrastructure.database.models import JobPostingModel
from ...application.dtos.job_dtos import (
    CreateJobDTO,
    UpdateJobDTO,
    JobDTO,
    JobSummaryDTO,
    JobFiltersDTO,
    JobSearchRequestDTO,
    JobSearchResponseDTO,
    AnalyzeJobResponseDTO,
    ConvertTextRequestDTO,
    JobTemplateDTO,
    UserJobListDTO,
)


class DatabaseJobRepository(JobRepositoryInterface):
    """Database-backed job repository for user-created and static jobs."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user_job(self, user_id: str, job: CreateJobDTO) -> JobDTO:
        """Insert a new user-created job into jobs table."""
        from ...application.services.job_description_parser import JobDescriptionParser
        
        job_id = str(uuid.uuid4())
        
        # Parse raw text if provided
        if job.raw_text:
            parser = JobDescriptionParser()
            parsed = parser.parse(job.raw_text)
            
            # Merge parsed data with provided structured data (structured data wins)
            job_data = {
                **parsed,  # Parsed from text
                **job.model_dump(exclude={"raw_text"}, exclude_none=True),  # Override
            }
            job_data["raw_text"] = job.raw_text
        else:
            # Use structured data directly
            job_data = job.model_dump(exclude_none=True)
        
        # Extract salary range
        salary_range = job_data.get("salary_range", {})
        
        stmt = insert(JobPostingModel).values(
            id=job_id,
            title=job_data.get("title", ""),
            company=job_data.get("company", ""),
            location=job_data.get("location", ""),
            description=job_data.get("description", ""),
            requirements=job_data.get("requirements", []),
            salary_min=salary_range.get('min') if salary_range else None,
            salary_max=salary_range.get('max') if salary_range else None,
            salary_currency=salary_range.get('currency', 'USD') if salary_range else 'USD',
            remote=job_data.get("remote", False),
            job_type=job_data.get("job_type", 'full_time'),
            experience_level=job_data.get("experience_level", 'entry'),
            posted_date=func.now(),
            application_url=None,
            source=job_data.get("source", 'user_created'),
            user_id=user_id,
            status='draft'
        )
        await self.session.execute(stmt)
        await self.session.commit()

        created_job = await self.get_job_by_id(job_id)
        if created_job is None:
            raise ValueError("Failed to create job")
        return created_job

    async def get_all_jobs(self) -> List[JobDTO]:
        q = await self.session.execute(select(JobPostingModel))
        rows = q.scalars().all()
        return [self._model_to_dto(m) for m in rows]

    async def get_job_by_id(self, job_id: str) -> Optional[JobDTO]:
        q = await self.session.execute(select(JobPostingModel).where(JobPostingModel.id == job_id))
        model = q.scalar_one_or_none()
        return self._model_to_dto(model) if model else None

    async def search_jobs(
        self,
        query: str = "",
        filters: Optional[JobFiltersDTO] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[JobDTO]:
        stmt = select(JobPostingModel).order_by(JobPostingModel.posted_date.desc()).limit(limit).offset(offset)
        q = await self.session.execute(stmt)
        models = q.scalars().all()
        return [self._model_to_dto(m) for m in models]

    async def get_job_filters(self) -> JobFiltersDTO:
        # Simple aggregates using SQL functions
        # For brevity, return empty sets if none
        job_types = [r[0] for r in await self.session.execute(select(func.distinct(JobPostingModel.job_type)))]
        experience_levels = [r[0] for r in await self.session.execute(select(func.distinct(JobPostingModel.experience_level)))]
        locations = [r[0] for r in await self.session.execute(select(func.distinct(JobPostingModel.location)))]
        industries = []
        return JobFiltersDTO(
            job_types=[jt for jt in job_types if jt],
            experience_levels=[el for el in experience_levels if el],
            remote_work_policies=["remote", "hybrid", "onsite"],
            industries=industries,
            company_sizes=[],
            locations=[loc for loc in locations if loc],
            tags=[],
            salary_ranges={}
        )

    async def get_filter_options(self) -> dict:
        dto = await self.get_job_filters()
        return dto.model_dump()

    async def get_statistics(self) -> dict:
        total = await self.session.scalar(select(func.count()).select_from(JobPostingModel))
        return {"total_jobs": int(total or 0)}

    async def get_total_count(self) -> int:
        total = await self.session.scalar(select(func.count()).select_from(JobPostingModel))
        return int(total or 0)

    async def get_user_jobs(self, user_id: str, limit: int = 20, offset: int = 0) -> UserJobListDTO:
        q = await self.session.execute(select(JobPostingModel).where(JobPostingModel.user_id == user_id).order_by(JobPostingModel.created_at.desc()).limit(limit).offset(offset))
        models = q.scalars().all()
        items = [self._model_to_dto(m) for m in models]
        total = await self.session.scalar(select(func.count()).select_from(JobPostingModel).where(JobPostingModel.user_id == user_id))
        return UserJobListDTO(items=items, total=int(total or 0), limit=limit, offset=offset)

    async def update_user_job(self, user_id: str, job_id: str, data: UpdateJobDTO) -> Optional[JobDTO]:
        # Ensure ownership by loading model
        model = await self.session.get(JobPostingModel, job_id)
        if not model or (model.user_id != user_id):
            return None

        values = {}
        payload = data.model_dump(exclude_none=True)
        if 'title' in payload:
            values['title'] = payload['title']
        if 'company' in payload:
            values['company'] = payload['company']
        if 'description' in payload:
            values['description'] = payload['description']
        if 'requirements' in payload:
            values['requirements'] = payload['requirements'] or []
        if 'location' in payload:
            values['location'] = payload['location']
        if 'remote' in payload:
            values['remote'] = payload['remote']
        if 'job_type' in payload and payload['job_type'] is not None:
            values['job_type'] = payload['job_type']
        if 'experience_level' in payload and payload['experience_level'] is not None:
            values['experience_level'] = payload['experience_level']
        if 'salary_range' in payload and payload['salary_range']:
            sr = payload['salary_range']
            values['salary_min'] = sr.get('min')
            values['salary_max'] = sr.get('max')
            values['salary_currency'] = sr.get('currency', 'USD')
        if 'status' in payload and payload['status']:
            values['status'] = payload['status']

        if not values:
            return self._model_to_dto(model)

        await self.session.execute(update(JobPostingModel).where(JobPostingModel.id == job_id).values(**values))
        await self.session.commit()
        return await self.get_job_by_id(job_id)

    async def delete_user_job(self, user_id: str, job_id: str) -> bool:
        model = await self.session.get(JobPostingModel, job_id)
        if not model or (model.user_id != user_id):
            return False
        await self.session.execute(delete(JobPostingModel).where(JobPostingModel.id == job_id))
        await self.session.commit()
        return True

    async def change_status(self, user_id: str, job_id: str, status: str) -> Optional[JobDTO]:
        if status not in ("draft", "active", "archived"):
            raise ValueError("Invalid status")
        model = await self.session.get(JobPostingModel, job_id)
        if not model or (model.user_id != user_id):
            return None
        await self.session.execute(update(JobPostingModel).where(JobPostingModel.id == job_id).values(status=status))
        await self.session.commit()
        return await self.get_job_by_id(job_id)

    async def analyze_job(self, job_id: str) -> AnalyzeJobResponseDTO:
        model = await self.session.get(JobPostingModel, job_id)
        if not model:
            raise ValueError("Job not found")

        # Use simple analysis like domain entity
        from ...domain.entities.job import JobPosting as DomainJob
        dj = DomainJob.create(
            id=model.id,
            title=model.title,
            company=model.company,
            location=model.location,
            description=model.description,
            requirements=model.requirements or [],
            job_type=model.job_type,
            experience_level=model.experience_level,
            posted_date=model.posted_date,
            remote=model.remote,
        )

        keywords = dj.extract_keywords()
        tech = dj.get_technical_requirements()
        soft = dj.get_soft_skills_requirements()
        difficulty = dj.estimate_match_difficulty()

        return AnalyzeJobResponseDTO(
            keywords=keywords,
            technical_skills=tech,
            soft_skills=soft,
            experience_level=str(model.experience_level.value) if model.experience_level else None,
            match_difficulty=difficulty
        )

    async def convert_text_to_job(self, raw_text: str) -> JobTemplateDTO:
        # Very simple conversion: split lines and pick first lines as title/company
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        title = lines[0] if lines else ""
        company = lines[1] if len(lines) > 1 else ""
        description = "\n".join(lines[2:]) if len(lines) > 2 else raw_text
        template = {
            "title": title,
            "company": company,
            "description": description,
            "requirements": [],
            "benefits": [],
            "location": "",
            "job_type": "full_time",
            "experience_level": "entry",
            "salary_range": None,
            "source": "user_converted"
        }
        return JobTemplateDTO(template=template)

    def _model_to_dto(self, model: JobPostingModel) -> JobDTO:
        if model is None:
            return None
        salary = None
        if model.salary_min or model.salary_max:
            salary = SalaryRangeDTO(
                min=model.salary_min or 0,
                max=model.salary_max or 0,
                currency=model.salary_currency or "USD"
            )

        return JobDTO(
            id=model.id,
            title=model.title,
            company=model.company,
            location=model.location,
            job_type=str(model.job_type.value) if model.job_type else "full-time",
            experience_level=str(model.experience_level.value) if model.experience_level else "entry",
            salary_range=salary,
            description=model.description,
            requirements=model.requirements or [],
            benefits=[],
            posted_date=model.posted_date,
            application_deadline=model.expires_date,
            company_size="50-200",  # Default valid value
            industry="Technology",  # Default valid value
            remote_work_policy=("remote" if model.remote else "onsite"),
            tags=[]
        )


class StaticJobRepository(JobRepositoryInterface):
    """Simple static JSON-backed repository used for tests and local data."""

    def __init__(self, data_file_path: str):
        self.data_file = Path(data_file_path)
        self._jobs_cache = []

    async def _ensure_loaded(self):
        if self._jobs_cache is None:
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self._jobs_cache = json.load(f)
            except Exception:
                self._jobs_cache = []

    async def search_jobs(self, query: str = "", filters: Optional[JobFiltersDTO] = None, limit: int = 20, offset: int = 0):
        await self._ensure_loaded()
        results = []
        q = (query or "").lower()
        for job in self._jobs_cache:
            if not q or q in job.get('title','').lower() or q in job.get('company','').lower() or q in job.get('description','').lower():
                results.append(job)

        return results[offset:offset+limit]

    async def get_job_by_id(self, job_id: str):
        await self._ensure_loaded()
        for job in self._jobs_cache:
            if job.get('id') == job_id:
                return job
        return None

    async def get_all_jobs(self):
        await self._ensure_loaded()
        return list(self._jobs_cache)

    async def get_job_filters(self):
        await self._ensure_loaded()
        job_types = sorted({j.get('job_type') for j in self._jobs_cache if j.get('job_type')})
        experience_levels = sorted({j.get('experience_level') for j in self._jobs_cache if j.get('experience_level')})
        locations = sorted({j.get('location') for j in self._jobs_cache if j.get('location')})
        return {
            'job_types': list(job_types),
            'experience_levels': list(experience_levels),
            'locations': list(locations),
            'companies': sorted({j.get('company') for j in self._jobs_cache if j.get('company')}),
            'salary_ranges': {}
        }

    # Backwards-compat alias
    async def get_filter_options(self):
        return await self.get_job_filters()

    async def get_statistics(self):
        await self._ensure_loaded()
        total = len(self._jobs_cache)
        return {
            'total_jobs': total,
            'active_jobs': total,
            'jobs_posted_today': 0,
            'jobs_posted_this_week': 0,
            'average_salary': 0
        }

    async def get_total_count(self):
        await self._ensure_loaded()
        return len(self._jobs_cache)
