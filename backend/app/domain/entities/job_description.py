"""Custom job description domain entity."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from enum import Enum


class JobDescriptionStatus(Enum):
    """Status of job description."""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class JobDescriptionSource(Enum):
    """Source of job description."""
    MANUAL = "manual"
    SCRAPED = "scraped"
    UPLOADED = "uploaded"


@dataclass
class JobDescriptionMetadata:
    """Metadata for job description."""
    keywords: List[str]
    technical_skills: List[str]
    soft_skills: List[str]
    experience_level: str
    industry: Optional[str]
    company_size: Optional[str]
    remote_policy: Optional[str]
    salary_range_min: Optional[int]
    salary_range_max: Optional[int]
    salary_currency: str
    location: Optional[str]
    created_from_url: Optional[str]

    @classmethod
    def create_empty(cls) -> 'JobDescriptionMetadata':
        """Create empty metadata."""
        return cls(
            keywords=[],
            technical_skills=[],
            soft_skills=[],
            experience_level="",
            industry=None,
            company_size=None,
            remote_policy=None,
            salary_range_min=None,
            salary_range_max=None,
            salary_currency="USD",
            location=None,
            created_from_url=None,
        )


@dataclass
class JobDescription:
    """Custom job description entity for resume generation."""
    id: UUID
    user_id: UUID
    title: str
    company: str
    description: str
    requirements: List[str]
    benefits: List[str]
    status: JobDescriptionStatus
    source: JobDescriptionSource
    metadata: JobDescriptionMetadata
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        user_id: UUID,
        title: str,
        company: str,
        description: str,
        requirements: Optional[List[str]] = None,
        benefits: Optional[List[str]] = None,
        source: JobDescriptionSource = JobDescriptionSource.MANUAL,
        metadata: Optional[JobDescriptionMetadata] = None,
        created_from_url: Optional[str] = None,
    ) -> 'JobDescription':
        """Create a new job description."""
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            user_id=user_id,
            title=title,
            company=company,
            description=description,
            requirements=requirements or [],
            benefits=benefits or [],
            status=JobDescriptionStatus.DRAFT,
            source=source,
            metadata=metadata or JobDescriptionMetadata.create_empty(),
            version=1,
            created_at=now,
            updated_at=now,
        )

    def update_content(
        self,
        title: Optional[str] = None,
        company: Optional[str] = None,
        description: Optional[str] = None,
        requirements: Optional[List[str]] = None,
        benefits: Optional[List[str]] = None,
    ) -> None:
        """Update job description content."""
        if title is not None:
            self.title = title
        if company is not None:
            self.company = company
        if description is not None:
            self.description = description
        if requirements is not None:
            self.requirements = requirements
        if benefits is not None:
            self.benefits = benefits

        self.updated_at = datetime.utcnow()
        self.version += 1

    def update_metadata(self, metadata: JobDescriptionMetadata) -> None:
        """Update job description metadata."""
        self.metadata = metadata
        self.updated_at = datetime.utcnow()
        self.version += 1

    def activate(self) -> None:
        """Mark job description as active."""
        self.status = JobDescriptionStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def archive(self) -> None:
        """Archive job description."""
        self.status = JobDescriptionStatus.ARCHIVED
        self.updated_at = datetime.utcnow()

    def extract_keywords(self) -> List[str]:
        """Extract keywords from job description."""
        keywords = set()

        # Extract from title
        title_words = self.title.lower().split()
        keywords.update(word for word in title_words if len(word) > 2)

        # Extract from requirements
        for req in self.requirements:
            req_words = req.lower().split()
            keywords.update(word for word in req_words if len(word) > 2)

        # Extract from description (simple approach)
        desc_words = self.description.lower().split()
        # Filter out common stop words
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        keywords.update(word for word in desc_words if word not in stop_words and len(word) > 2)

        return sorted(list(keywords))

    def get_technical_requirements(self) -> List[str]:
        """Get technical skill requirements."""
        technical_keywords = {
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node', 'django', 'flask',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'aws', 'azure', 'gcp', 'docker',
            'kubernetes', 'git', 'linux', 'windows', 'api', 'rest', 'graphql', 'html', 'css',
            'typescript', 'c++', 'c#', '.net', 'php', 'ruby', 'go', 'rust', 'scala', 'kotlin',
            'machine learning', 'ai', 'ml', 'data science', 'tensorflow', 'pytorch', 'pandas',
            'numpy', 'scikit-learn', 'jupyter', 'spark', 'hadoop', 'kafka', 'elasticsearch'
        }

        tech_reqs = []
        all_text = ' '.join([self.title, self.description] + self.requirements).lower()

        for keyword in technical_keywords:
            if keyword in all_text:
                tech_reqs.append(keyword.title())

        return list(set(tech_reqs))

    def get_soft_skills_requirements(self) -> List[str]:
        """Get soft skills requirements."""
        soft_keywords = {
            'communication', 'leadership', 'teamwork', 'problem solving', 'analytical',
            'organization', 'time management', 'adaptability', 'creativity', 'collaboration',
            'interpersonal', 'presentation', 'project management', 'critical thinking',
            'attention to detail', 'flexibility', 'initiative', 'mentoring', 'coaching'
        }

        soft_reqs = []
        all_text = ' '.join([self.title, self.description] + self.requirements).lower()

        for keyword in soft_keywords:
            if keyword in all_text:
                soft_reqs.append(keyword.title())

        return list(set(soft_reqs))

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'title': self.title,
            'company': self.company,
            'description': self.description,
            'requirements': self.requirements,
            'benefits': self.benefits,
            'status': self.status.value,
            'source': self.source.value,
            'metadata': {
                'keywords': self.metadata.keywords,
                'technical_skills': self.metadata.technical_skills,
                'soft_skills': self.metadata.soft_skills,
                'experience_level': self.metadata.experience_level,
                'industry': self.metadata.industry,
                'company_size': self.metadata.company_size,
                'remote_policy': self.metadata.remote_policy,
                'salary_range_min': self.metadata.salary_range_min,
                'salary_range_max': self.metadata.salary_range_max,
                'salary_currency': self.metadata.salary_currency,
                'location': self.metadata.location,
                'created_from_url': self.metadata.created_from_url,
            },
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }