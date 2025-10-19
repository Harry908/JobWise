"""Experience value object."""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass(frozen=True)
class Experience:
    """Work experience value object."""
    title: str
    company: str
    location: Optional[str]
    start_date: date
    end_date: Optional[date]
    is_current: bool
    description: str
    achievements: List[str]

    def __post_init__(self):
        """Validate experience."""
        if not self.title or not self.title.strip():
            raise ValueError("Job title is required")
        if not self.company or not self.company.strip():
            raise ValueError("Company is required")
        if not self.description or not self.description.strip():
            raise ValueError("Description is required")

        # Validate dates
        if self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")

        # If current position, end_date should be None
        if self.is_current and self.end_date is not None:
            raise ValueError("Current position should not have end date")

    def get_duration_months(self) -> int:
        """Calculate duration in months."""
        end = self.end_date if self.end_date else date.today()
        months = (end.year - self.start_date.year) * 12 + (end.month - self.start_date.month)
        return max(0, months)

    def get_duration_years(self) -> float:
        """Calculate duration in years."""
        return round(self.get_duration_months() / 12.0, 1)

    def get_technologies(self) -> List[str]:
        """Extract technologies from description (simple approach)."""
        # This would be more sophisticated in real implementation
        tech_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node',
            'django', 'flask', 'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git'
        ]

        found_tech = []
        desc_lower = self.description.lower()
        for tech in tech_keywords:
            if tech in desc_lower:
                found_tech.append(tech.title())

        return found_tech

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_current': self.is_current,
            'description': self.description,
            'achievements': self.achievements,
        }