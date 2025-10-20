"""Domain entities for the JobWise application."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from ..value_objects import (
    PersonalInfo, Experience, Education, Skills, Project
)


@dataclass
class MasterProfile:
    """Master resume profile entity."""
    id: UUID
    user_id: UUID
    personal_info: PersonalInfo
    professional_summary: Optional[str]
    experiences: List[Experience]
    education: List[Education]
    skills: Skills
    projects: List[Project]
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        user_id: UUID,
        personal_info: PersonalInfo,
        professional_summary: Optional[str] = None,
        experiences: Optional[List[Experience]] = None,
        education: Optional[List[Education]] = None,
        skills: Optional[Skills] = None,
        projects: Optional[List[Project]] = None,
    ) -> 'MasterProfile':
        """Create a new master profile."""
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            user_id=user_id,
            personal_info=personal_info,
            professional_summary=professional_summary,
            experiences=experiences or [],
            education=education or [],
            skills=skills or Skills.create_empty(),
            projects=projects or [],
            version=1,
            created_at=now,
            updated_at=now,
        )

    def update_personal_info(self, personal_info: PersonalInfo) -> None:
        """Update personal information."""
        self.personal_info = personal_info
        self.updated_at = datetime.utcnow()
        self.version += 1

    def update_professional_summary(self, summary: str) -> None:
        """Update professional summary."""
        self.professional_summary = summary
        self.updated_at = datetime.utcnow()
        self.version += 1

    def add_experience(self, experience: Experience) -> None:
        """Add work experience."""
        self.experiences.append(experience)
        self.updated_at = datetime.utcnow()
        self.version += 1

    def update_experience(self, index: int, experience: Experience) -> None:
        """Update work experience at index."""
        if 0 <= index < len(self.experiences):
            self.experiences[index] = experience
            self.updated_at = datetime.utcnow()
            self.version += 1
        else:
            raise ValueError("Invalid experience index")

    def remove_experience(self, index: int) -> None:
        """Remove work experience at index."""
        if 0 <= index < len(self.experiences):
            self.experiences.pop(index)
            self.updated_at = datetime.utcnow()
            self.version += 1
        else:
            raise ValueError("Invalid experience index")

    def add_education(self, education: Education) -> None:
        """Add education."""
        self.education.append(education)
        self.updated_at = datetime.utcnow()
        self.version += 1

    def update_education(self, index: int, education: Education) -> None:
        """Update education at index."""
        if 0 <= index < len(self.education):
            self.education[index] = education
            self.updated_at = datetime.utcnow()
            self.version += 1
        else:
            raise ValueError("Invalid education index")

    def remove_education(self, index: int) -> None:
        """Remove education at index."""
        if 0 <= index < len(self.education):
            self.education.pop(index)
            self.updated_at = datetime.utcnow()
            self.version += 1
        else:
            raise ValueError("Invalid education index")

    def update_skills(self, skills: Skills) -> None:
        """Update skills."""
        self.skills = skills
        self.updated_at = datetime.utcnow()
        self.version += 1

    def add_project(self, project: Project) -> None:
        """Add project."""
        self.projects.append(project)
        self.updated_at = datetime.utcnow()
        self.version += 1

    def update_project(self, index: int, project: Project) -> None:
        """Update project at index."""
        if 0 <= index < len(self.projects):
            self.projects[index] = project
            self.updated_at = datetime.utcnow()
            self.version += 1
        else:
            raise ValueError("Invalid project index")

    def remove_project(self, index: int) -> None:
        """Remove project at index."""
        if 0 <= index < len(self.projects):
            self.projects.pop(index)
            self.updated_at = datetime.utcnow()
            self.version += 1
        else:
            raise ValueError("Invalid project index")

    def get_relevant_experiences(self, keywords: List[str]) -> List[Experience]:
        """Get experiences relevant to keywords."""
        relevant = []
        for exp in self.experiences:
            if any(keyword.lower() in exp.description.lower() for keyword in keywords):
                relevant.append(exp)
        return relevant

    def get_technical_skills(self) -> List[str]:
        """Get all technical skills."""
        return self.skills.get_all_technical_skills()

    def calculate_years_experience(self) -> float:
        """Calculate total years of professional experience."""
        total_months = 0
        for exp in self.experiences:
            start = exp.start_date
            end = exp.end_date if exp.end_date else datetime.now().date()
            months = (end.year - start.year) * 12 + (end.month - start.month)
            total_months += max(0, months)
        return round(total_months / 12.0, 1)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'personal_info': {
                'full_name': self.personal_info.full_name,
                'email': self.personal_info.email,
                'phone': self.personal_info.phone,
                'location': self.personal_info.location,
                'linkedin': self.personal_info.linkedin,
                'github': self.personal_info.github,
                'website': self.personal_info.website,
            },
            'professional_summary': self.professional_summary,
            'experiences': [
                {
                    'title': exp.title,
                    'company': exp.company,
                    'location': exp.location,
                    'start_date': exp.start_date.isoformat(),
                    'end_date': exp.end_date.isoformat() if exp.end_date else None,
                    'is_current': exp.is_current,
                    'description': exp.description,
                    'achievements': exp.achievements,
                }
                for exp in self.experiences
            ],
            'education': [
                {
                    'institution': edu.institution,
                    'degree': edu.degree,
                    'field_of_study': edu.field_of_study,
                    'start_date': edu.start_date.isoformat(),
                    'end_date': edu.end_date.isoformat() if edu.end_date else None,
                    'gpa': edu.gpa,
                    'honors': edu.honors,
                }
                for edu in self.education
            ],
            'skills': {
                'technical': self.skills.get_all_technical_skills(),
                'soft': self.skills.get_all_soft_skills(),
                'languages': [
                    {'name': lang.name, 'proficiency': lang.proficiency.value}
                    for lang in self.skills.get_all_languages()
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
                    for cert in self.skills.get_all_certifications()
                ],
            },
            'projects': [
                {
                    'name': proj.name,
                    'description': proj.description,
                    'technologies': proj.technologies,
                    'url': proj.url,
                    'start_date': proj.start_date.isoformat() if proj.start_date else None,
                    'end_date': proj.end_date.isoformat() if proj.end_date else None,
                }
                for proj in self.projects
            ],
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }