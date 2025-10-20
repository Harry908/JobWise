"""Education value object."""

from dataclasses import dataclass
from datetime import date
from typing import Optional, List


@dataclass(frozen=True)
class Education:
    """Education value object."""
    institution: str
    degree: str
    field_of_study: str
    start_date: date
    end_date: Optional[date]
    gpa: Optional[float]
    honors: List[str]

    def __post_init__(self):
        """Validate education."""
        if not self.institution or not self.institution.strip():
            raise ValueError("Institution is required")
        if not self.degree or not self.degree.strip():
            raise ValueError("Degree is required")
        if not self.field_of_study or not self.field_of_study.strip():
            raise ValueError("Field of study is required")

        # Validate dates
        if self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")

        # Validate GPA
        if self.gpa is not None and (self.gpa < 0.0 or self.gpa > 4.0):
            raise ValueError("GPA must be between 0.0 and 4.0")

    def get_duration_months(self) -> int:
        """Calculate duration in months."""
        end = self.end_date if self.end_date else date.today()
        months = (end.year - self.start_date.year) * 12 + (end.month - self.start_date.month)
        return max(0, months)

    def get_duration_years(self) -> float:
        """Calculate duration in years."""
        return round(self.get_duration_months() / 12.0, 1)

    def is_completed(self) -> bool:
        """Check if education is completed."""
        return self.end_date is not None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'institution': self.institution,
            'degree': self.degree,
            'field_of_study': self.field_of_study,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'gpa': self.gpa,
            'honors': self.honors,
        }