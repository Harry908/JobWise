"""Value objects for the JobWise domain."""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional
from enum import Enum


class SkillCategory(Enum):
    """Categories for skills."""
    TECHNICAL = "technical"
    SOFT = "soft"
    LANGUAGE = "language"
    CERTIFICATION = "certification"


class ProficiencyLevel(Enum):
    """Proficiency levels for skills."""
    BASIC = "basic"
    CONVERSATIONAL = "conversational"
    FLUENT = "fluent"
    NATIVE = "native"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass(frozen=True)
class PersonalInfo:
    """Personal information value object."""
    full_name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None

    def __post_init__(self):
        """Validate personal info."""
        if not self.full_name or not self.full_name.strip():
            raise ValueError("Full name is required")
        if not self.email or "@" not in self.email:
            raise ValueError("Valid email is required")


@dataclass(frozen=True)
class Experience:
    """Work experience value object."""
    title: str
    company: str
    start_date: date
    description: str
    achievements: List[str]
    location: Optional[str] = None
    end_date: Optional[date] = None
    is_current: bool = False

    def __post_init__(self):
        """Validate experience."""
        if not self.title or not self.title.strip():
            raise ValueError("Job title is required")
        if not self.company or not self.company.strip():
            raise ValueError("Company name is required")
        if not self.description or not self.description.strip():
            raise ValueError("Job description is required")
        if self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")
        if self.is_current and self.end_date:
            raise ValueError("Current position cannot have end date")


@dataclass(frozen=True)
class Education:
    """Education value object."""
    institution: str
    degree: str
    field_of_study: str
    start_date: date
    end_date: Optional[date] = None
    gpa: Optional[float] = None
    honors: Optional[List[str]] = None

    def __post_init__(self):
        """Validate education."""
        if not self.institution or not self.institution.strip():
            raise ValueError("Institution is required")
        if not self.degree or not self.degree.strip():
            raise ValueError("Degree is required")
        if not self.field_of_study or not self.field_of_study.strip():
            raise ValueError("Field of study is required")
        if self.gpa is not None and (self.gpa < 0.0 or self.gpa > 4.0):
            raise ValueError("GPA must be between 0.0 and 4.0")
        if self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")

    def __defaults__(self):
        if self.honors is None:
            object.__setattr__(self, 'honors', [])


@dataclass(frozen=True)
class Language:
    """Language proficiency value object."""
    name: str
    proficiency: ProficiencyLevel

    def __post_init__(self):
        """Validate language."""
        if not self.name or not self.name.strip():
            raise ValueError("Language name is required")


@dataclass(frozen=True)
class Certification:
    """Certification value object."""
    name: str
    issuer: str
    date_obtained: date
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None
    verification_url: Optional[str] = None

    def __post_init__(self):
        """Validate certification."""
        if not self.name or not self.name.strip():
            raise ValueError("Certification name is required")
        if not self.issuer or not self.issuer.strip():
            raise ValueError("Issuer is required")
        if self.expiry_date and self.date_obtained > self.expiry_date:
            raise ValueError("Date obtained cannot be after expiry date")


@dataclass(frozen=True)
class Skill:
    """Individual skill value object."""
    name: str
    category: SkillCategory
    proficiency_level: Optional[ProficiencyLevel] = None
    years_experience: Optional[float] = None

    def __post_init__(self):
        """Validate skill."""
        if not self.name or not self.name.strip():
            raise ValueError("Skill name is required")
        if self.years_experience is not None and self.years_experience < 0:
            raise ValueError("Years of experience cannot be negative")


@dataclass(frozen=True)
class Skills:
    """Skills collection value object."""
    technical: Optional[List[str]] = None
    soft: Optional[List[str]] = None
    languages: Optional[List[Language]] = None
    certifications: Optional[List[Certification]] = None

    def __post_init__(self):
        """Initialize empty lists if None."""
        if self.technical is None:
            object.__setattr__(self, 'technical', [])
        if self.soft is None:
            object.__setattr__(self, 'soft', [])
        if self.languages is None:
            object.__setattr__(self, 'languages', [])
        if self.certifications is None:
            object.__setattr__(self, 'certifications', [])

    def get_all_technical_skills(self) -> List[str]:
        """Get all technical skills."""
        return self.technical.copy() if self.technical else []

    def get_all_soft_skills(self) -> List[str]:
        """Get all soft skills."""
        return self.soft.copy() if self.soft else []

    def get_all_languages(self) -> List[Language]:
        """Get all languages."""
        return self.languages.copy() if self.languages else []

    def get_all_certifications(self) -> List[Certification]:
        """Get all certifications."""
        return self.certifications.copy() if self.certifications else []


@dataclass(frozen=True)
class Project:
    """Project value object."""
    name: str
    description: str
    technologies: Optional[List[str]] = None
    url: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    def __post_init__(self):
        """Validate project."""
        if not self.name or not self.name.strip():
            raise ValueError("Project name is required")
        if not self.description or not self.description.strip():
            raise ValueError("Project description is required")
        if self.end_date and self.start_date and self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")

    def __defaults__(self):
        if self.technologies is None:
            object.__setattr__(self, 'technologies', [])


@dataclass(frozen=True)
class SalaryRange:
    """Salary range value object."""
    min: int
    max: int
    currency: str = "USD"

    def __post_init__(self):
        """Validate salary range."""
        if self.min < 0:
            raise ValueError("Minimum salary cannot be negative")
        if self.max < self.min:
            raise ValueError("Maximum salary cannot be less than minimum")


@dataclass(frozen=True)
class ContactInfo:
    """Contact information value object."""
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None

    def __post_init__(self):
        """Validate contact info."""
        if not self.email or "@" not in self.email:
            raise ValueError("Valid email is required")