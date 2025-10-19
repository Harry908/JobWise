"""Personal information value object."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PersonalInfo:
    """Personal information value object."""
    full_name: str
    email: str
    phone: Optional[str]
    location: Optional[str]
    linkedin: Optional[str]
    github: Optional[str]
    website: Optional[str]

    def __post_init__(self):
        """Validate personal info."""
        if not self.full_name or not self.full_name.strip():
            raise ValueError("Full name is required")
        if not self.email or not self.email.strip():
            raise ValueError("Email is required")
        if "@" not in self.email:
            raise ValueError("Invalid email format")

    def get_display_name(self) -> str:
        """Get display name."""
        return self.full_name

    def get_contact_info(self) -> dict:
        """Get contact information."""
        return {
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
        }

    def get_social_links(self) -> dict:
        """Get social media links."""
        return {
            'linkedin': self.linkedin,
            'github': self.github,
            'website': self.website,
        }