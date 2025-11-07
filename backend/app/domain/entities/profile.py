"""Profile domain entities."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
import uuid


class PersonalInfo(BaseModel):
    """Personal information model."""
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=100)
    linkedin: Optional[str] = Field(None, max_length=200)
    github: Optional[str] = Field(None, max_length=200)
    website: Optional[str] = Field(None, max_length=200)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Basic phone validation."""
        if v and not any(char.isdigit() for char in v):
            raise ValueError('Phone must contain at least one digit')
        return v

    @field_validator('linkedin', 'github', 'website')
    @classmethod
    def validate_url(cls, v):
        """Basic URL validation."""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class Language(BaseModel):
    """Language proficiency model."""
    name: str = Field(..., min_length=1, max_length=50)
    proficiency: str = Field(..., pattern=r'^(native|fluent|conversational|basic)$')


class Certification(BaseModel):
    """Certification model."""
    name: str = Field(..., min_length=1, max_length=200)
    issuer: str = Field(..., min_length=1, max_length=100)
    date_obtained: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')  # ISO date
    expiry_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')  # ISO date
    credential_id: Optional[str] = Field(None, max_length=100)


class Skills(BaseModel):
    """Skills model."""
    technical: List[str] = Field(default_factory=list)
    soft: List[str] = Field(default_factory=list)
    languages: List[Language] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)

    @field_validator('technical', 'soft')
    @classmethod
    def validate_skill_lists(cls, v):
        """Validate skill lists are not empty strings."""
        if v:
            for skill in v:
                if not skill.strip():
                    raise ValueError('Skills cannot be empty strings')
        return v


class Experience(BaseModel):
    """Work experience model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=1, max_length=100)
    company: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    start_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')  # ISO date
    end_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')  # ISO date
    is_current: bool = False
    description: Optional[str] = Field(None, max_length=2000)
    achievements: List[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_dates(self):
        """Validate date logic."""
        if self.end_date and self.start_date > self.end_date:
            raise ValueError('Start date cannot be after end date')
        if self.is_current and self.end_date:
            raise ValueError('Current position cannot have end date')
        # Allow past positions without end date for flexibility
        # if not self.is_current and not self.end_date:
        #     raise ValueError('Past position must have end date')
        return self


class Education(BaseModel):
    """Education model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    institution: str = Field(..., min_length=1, max_length=100)
    degree: str = Field(..., min_length=1, max_length=100)
    field_of_study: str = Field(..., min_length=1, max_length=100)
    start_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')  # ISO date
    end_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')  # ISO date, optional
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    honors: List[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_dates(self):
        """Validate date logic."""
        if self.end_date and self.start_date >= self.end_date:
            raise ValueError('Start date must be before end date')
        return self


class Project(BaseModel):
    """Project model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    technologies: List[str] = Field(default_factory=list)
    url: Optional[str] = Field(None, max_length=200)
    start_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')  # ISO date, optional
    end_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')  # ISO date, optional

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        """Basic URL validation - auto-prefix with http:// if needed."""
        if v and v.strip():
            # If it looks like a URL but missing protocol, add http://
            if not (v.startswith('http://') or v.startswith('https://')):
                # Only add protocol if it looks like a URL (contains dots or is a domain-like string)
                if '.' in v or v.startswith('www.'):
                    return f'http://{v}'
                else:
                    # For non-URL strings like 'asdf', just allow them as-is (could be project names, etc.)
                    return v
        return v

    @model_validator(mode='after')
    def validate_dates(self):
        """Validate date logic."""
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError('Start date cannot be after end date')
        return self


class Profile(BaseModel):
    """Master profile model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int
    personal_info: PersonalInfo
    professional_summary: Optional[str] = Field(None, max_length=2000)
    experiences: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: Skills
    projects: List[Project] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode='after')
    def validate_profile_completeness(self):
        """Ensure profile has minimum required data."""
        if not self.personal_info.full_name.strip():
            raise ValueError('Full name is required')
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Profile':
        """Create from dictionary."""
        return cls.model_validate(data)