"""Project value object."""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass(frozen=True)
class Project:
    """Project value object."""
    name: str
    description: str
    technologies: List[str]
    url: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]

    def __post_init__(self):
        """Validate project."""
        if not self.name or not self.name.strip():
            raise ValueError("Project name is required")
        if not self.description or not self.description.strip():
            raise ValueError("Project description is required")

        # Validate dates
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")

        # Validate URL format (basic check)
        if self.url and not (self.url.startswith('http://') or self.url.startswith('https://')):
            raise ValueError("URL must start with http:// or https://")

    def get_duration_months(self) -> Optional[int]:
        """Calculate duration in months."""
        if not self.start_date:
            return None

        end = self.end_date if self.end_date else date.today()
        months = (end.year - self.start_date.year) * 12 + (end.month - self.start_date.month)
        return max(0, months)

    def get_duration_years(self) -> Optional[float]:
        """Calculate duration in years."""
        months = self.get_duration_months()
        return round(months / 12.0, 1) if months is not None else None

    def is_completed(self) -> bool:
        """Check if project is completed."""
        return self.end_date is not None

    def is_ongoing(self) -> bool:
        """Check if project is ongoing."""
        return self.end_date is None

    def get_technologies_string(self) -> str:
        """Get technologies as comma-separated string."""
        return ', '.join(self.technologies)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'technologies': self.technologies,
            'url': self.url,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
        }