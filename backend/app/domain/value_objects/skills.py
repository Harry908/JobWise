"""Skills value object."""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional
from enum import Enum


class ProficiencyLevel(Enum):
    """Skill proficiency levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SkillCategory(Enum):
    """Skill categories."""
    TECHNICAL = "technical"
    SOFT = "soft"
    LANGUAGE = "language"
    CERTIFICATION = "certification"


class LanguageProficiency(Enum):
    """Language proficiency levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    FLUENT = "fluent"
    NATIVE = "native"


@dataclass(frozen=True)
class Language:
    """Language skill."""
    name: str
    proficiency: LanguageProficiency

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
    expiry_date: Optional[date]
    credential_id: Optional[str]
    verification_url: Optional[str]

    def __post_init__(self):
        """Validate certification."""
        if not self.name or not self.name.strip():
            raise ValueError("Certification name is required")
        if not self.issuer or not self.issuer.strip():
            raise ValueError("Issuer is required")

        # Validate dates
        if self.expiry_date and self.date_obtained > self.expiry_date:
            raise ValueError("Date obtained cannot be after expiry date")

    def is_expired(self) -> bool:
        """Check if certification is expired."""
        if not self.expiry_date:
            return False
        return date.today() > self.expiry_date

    def is_valid(self) -> bool:
        """Check if certification is still valid."""
        return not self.is_expired()


@dataclass(frozen=True)
class Skills:
    """Skills value object."""
    technical_skills: List[str]
    soft_skills: List[str]
    languages: List[Language]
    certifications: List[Certification]

    def __post_init__(self):
        """Validate skills."""
        # Ensure no duplicates in technical skills
        if len(self.technical_skills) != len(set(self.technical_skills)):
            raise ValueError("Technical skills cannot contain duplicates")

        # Ensure no duplicates in soft skills
        if len(self.soft_skills) != len(set(self.soft_skills)):
            raise ValueError("Soft skills cannot contain duplicates")

        # Ensure no duplicate languages
        language_names = [lang.name.lower() for lang in self.languages]
        if len(language_names) != len(set(language_names)):
            raise ValueError("Languages cannot contain duplicates")

        # Ensure no duplicate certifications
        cert_names = [cert.name.lower() for cert in self.certifications]
        if len(cert_names) != len(set(cert_names)):
            raise ValueError("Certifications cannot contain duplicates")

    @classmethod
    def create_empty(cls) -> 'Skills':
        """Create empty skills."""
        return cls(
            technical_skills=[],
            soft_skills=[],
            languages=[],
            certifications=[],
        )

    def get_all_technical_skills(self) -> List[str]:
        """Get all technical skills."""
        return self.technical_skills.copy()

    def get_all_soft_skills(self) -> List[str]:
        """Get all soft skills."""
        return self.soft_skills.copy()

    def get_all_languages(self) -> List[Language]:
        """Get all languages."""
        return self.languages.copy()

    def get_all_certifications(self) -> List[Certification]:
        """Get all certifications."""
        return self.certifications.copy()

    def add_technical_skill(self, skill: str) -> 'Skills':
        """Add a technical skill."""
        if skill in self.technical_skills:
            return self
        return Skills(
            technical_skills=self.technical_skills + [skill],
            soft_skills=self.soft_skills,
            languages=self.languages,
            certifications=self.certifications,
        )

    def remove_technical_skill(self, skill: str) -> 'Skills':
        """Remove a technical skill."""
        return Skills(
            technical_skills=[s for s in self.technical_skills if s != skill],
            soft_skills=self.soft_skills,
            languages=self.languages,
            certifications=self.certifications,
        )

    def add_soft_skill(self, skill: str) -> 'Skills':
        """Add a soft skill."""
        if skill in self.soft_skills:
            return self
        return Skills(
            technical_skills=self.technical_skills,
            soft_skills=self.soft_skills + [skill],
            languages=self.languages,
            certifications=self.certifications,
        )

    def remove_soft_skill(self, skill: str) -> 'Skills':
        """Remove a soft skill."""
        return Skills(
            technical_skills=self.technical_skills,
            soft_skills=[s for s in self.soft_skills if s != skill],
            languages=self.languages,
            certifications=self.certifications,
        )

    def add_language(self, language: Language) -> 'Skills':
        """Add a language."""
        if any(lang.name.lower() == language.name.lower() for lang in self.languages):
            return self
        return Skills(
            technical_skills=self.technical_skills,
            soft_skills=self.soft_skills,
            languages=self.languages + [language],
            certifications=self.certifications,
        )

    def remove_language(self, language_name: str) -> 'Skills':
        """Remove a language."""
        return Skills(
            technical_skills=self.technical_skills,
            soft_skills=self.soft_skills,
            languages=[lang for lang in self.languages if lang.name.lower() != language_name.lower()],
            certifications=self.certifications,
        )

    def add_certification(self, certification: Certification) -> 'Skills':
        """Add a certification."""
        if any(cert.name.lower() == certification.name.lower() for cert in self.certifications):
            return self
        return Skills(
            technical_skills=self.technical_skills,
            soft_skills=self.soft_skills,
            languages=self.languages,
            certifications=self.certifications + [certification],
        )

    def remove_certification(self, certification_name: str) -> 'Skills':
        """Remove a certification."""
        return Skills(
            technical_skills=self.technical_skills,
            soft_skills=self.soft_skills,
            languages=self.languages,
            certifications=[cert for cert in self.certifications if cert.name.lower() != certification_name.lower()],
        )

    def get_valid_certifications(self) -> List[Certification]:
        """Get only valid (non-expired) certifications."""
        return [cert for cert in self.certifications if cert.is_valid()]

    def get_expired_certifications(self) -> List[Certification]:
        """Get expired certifications."""
        return [cert for cert in self.certifications if cert.is_expired()]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'technical_skills': self.technical_skills,
            'soft_skills': self.soft_skills,
            'languages': [
                {'name': lang.name, 'proficiency': lang.proficiency.value}
                for lang in self.languages
            ],
            'certifications': [
                {
                    'name': cert.name,
                    'issuer': cert.issuer,
                    'date_obtained': cert.date_obtained.isoformat(),
                    'expiry_date': cert.expiry_date.isoformat() if cert.expiry_date else None,
                    'credential_id': cert.credential_id,
                    'verification_url': cert.verification_url,
                }
                for cert in self.certifications
            ],
        }