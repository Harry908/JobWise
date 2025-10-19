"""Salary range value object."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SalaryRange:
    """Salary range value object."""
    min: Optional[float]
    max: Optional[float]
    currency: str

    def __post_init__(self):
        """Validate salary range."""
        if not self.currency or not self.currency.strip():
            raise ValueError("Currency is required")

        if self.min is not None and self.min < 0:
            raise ValueError("Minimum salary cannot be negative")

        if self.max is not None and self.max < 0:
            raise ValueError("Maximum salary cannot be negative")

        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError("Minimum salary cannot be greater than maximum salary")

    def get_midpoint(self) -> Optional[float]:
        """Calculate salary midpoint."""
        if self.min is None or self.max is None:
            return None
        return (self.min + self.max) / 2

    def get_range_string(self) -> str:
        """Get formatted salary range string."""
        if self.min is None and self.max is None:
            return f"Salary not specified ({self.currency})"

        min_str = f"{self.min:,.0f}" if self.min else "Not specified"
        max_str = f"{self.max:,.0f}" if self.max else "Not specified"

        return f"{min_str} - {max_str} {self.currency}"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'min': self.min,
            'max': self.max,
            'currency': self.currency,
        }