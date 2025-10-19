"""Job posting domain entity."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum

from ..value_objects import SalaryRange


class JobType(Enum):
    """Job employment types."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"


class ExperienceLevel(Enum):
    """Experience level requirements."""
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


@dataclass
class JobPosting:
    """Job posting entity."""
    id: str
    title: str
    company: str
    location: str
    description: str
    requirements: List[str]
    salary_range: Optional[SalaryRange]
    remote: bool
    job_type: JobType
    experience_level: ExperienceLevel
    posted_date: datetime
    expires_date: Optional[datetime]
    application_url: Optional[str]
    source: str

    @classmethod
    def create(
        cls,
        id: str,
        title: str,
        company: str,
        location: str,
        description: str,
        requirements: List[str],
        job_type: JobType,
        experience_level: ExperienceLevel,
        posted_date: datetime,
        remote: bool = False,
        salary_range: Optional[SalaryRange] = None,
        expires_date: Optional[datetime] = None,
        application_url: Optional[str] = None,
        source: str = "unknown",
    ) -> 'JobPosting':
        """Create a new job posting."""
        return cls(
            id=id,
            title=title,
            company=company,
            location=location,
            description=description,
            requirements=requirements,
            salary_range=salary_range,
            remote=remote,
            job_type=job_type,
            experience_level=experience_level,
            posted_date=posted_date,
            expires_date=expires_date,
            application_url=application_url,
            source=source,
        )

    def extract_keywords(self) -> List[str]:
        """Extract ATS keywords from job description and requirements."""
        # Simple keyword extraction - in real implementation this would be more sophisticated
        keywords = set()

        # Add requirements as keywords
        for req in self.requirements:
            words = req.lower().split()
            keywords.update(words)

        # Extract from description (simple approach)
        desc_words = self.description.lower().split()
        # Filter out common stop words and keep potential keywords
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        keywords.update(word for word in desc_words if word not in stop_words and len(word) > 2)

        return list(keywords)

    def get_technical_requirements(self) -> List[str]:
        """Get technical skill requirements."""
        # Simple filtering - in real implementation this would use NLP
        technical_keywords = {
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node', 'django', 'flask',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'aws', 'azure', 'gcp', 'docker',
            'kubernetes', 'git', 'linux', 'windows', 'api', 'rest', 'graphql', 'html', 'css',
            'typescript', 'c++', 'c#', '.net', 'php', 'ruby', 'go', 'rust', 'scala', 'kotlin'
        }

        tech_reqs = []
        for req in self.requirements:
            req_lower = req.lower()
            if any(keyword in req_lower for keyword in technical_keywords):
                tech_reqs.append(req)

        return tech_reqs

    def get_soft_skills_requirements(self) -> List[str]:
        """Get soft skills requirements."""
        # Simple filtering for soft skills
        soft_keywords = {
            'communication', 'leadership', 'teamwork', 'problem solving', 'analytical',
            'organization', 'time management', 'adaptability', 'creativity', 'collaboration',
            'interpersonal', 'presentation', 'project management', 'critical thinking'
        }

        soft_reqs = []
        for req in self.requirements:
            req_lower = req.lower()
            if any(keyword in req_lower for keyword in soft_keywords):
                soft_reqs.append(req)

        return soft_reqs

    def estimate_match_difficulty(self) -> float:
        """Estimate how difficult it is to match this job (0-1 scale)."""
        # Simple heuristic based on experience level and requirements count
        base_difficulty = {
            ExperienceLevel.ENTRY: 0.2,
            ExperienceLevel.MID: 0.5,
            ExperienceLevel.SENIOR: 0.7,
            ExperienceLevel.LEAD: 0.8,
            ExperienceLevel.EXECUTIVE: 0.9,
        }

        difficulty = base_difficulty.get(self.experience_level, 0.5)

        # Increase difficulty based on number of requirements
        req_count = len(self.requirements)
        if req_count > 10:
            difficulty += 0.2
        elif req_count > 5:
            difficulty += 0.1

        return min(1.0, difficulty)

    def is_expired(self) -> bool:
        """Check if the job posting has expired."""
        if not self.expires_date:
            return False
        return datetime.utcnow() > self.expires_date

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'remote': self.remote,
            'job_type': self.job_type.value,
            'experience_level': self.experience_level.value,
            'salary_range': {
                'min': self.salary_range.min if self.salary_range else None,
                'max': self.salary_range.max if self.salary_range else None,
                'currency': self.salary_range.currency if self.salary_range else None,
            } if self.salary_range else None,
            'description': self.description,
            'requirements': self.requirements,
            'posted_date': self.posted_date.isoformat(),
            'expires_date': self.expires_date.isoformat() if self.expires_date else None,
            'application_url': self.application_url,
            'source': self.source,
        }