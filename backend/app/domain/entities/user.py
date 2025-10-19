"""User domain entity for authentication and user management."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
import re


@dataclass
class User:
    """User entity for authentication and profile management."""
    id: UUID
    email: str
    hashed_password: str
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        email: str,
        hashed_password: str,
        full_name: str,
    ) -> 'User':
        """Create a new user."""
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            email=cls._normalize_email(email),
            hashed_password=hashed_password,
            full_name=full_name.strip(),
            is_active=True,
            is_verified=False,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _normalize_email(email: str) -> str:
        """Normalize email address."""
        return email.lower().strip()

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password strength."""
        # At least 8 characters, 1 uppercase, 1 lowercase, 1 digit
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True

    def update_profile(self, full_name: Optional[str] = None) -> None:
        """Update user profile information."""
        if full_name is not None:
            self.full_name = full_name.strip()
        self.updated_at = datetime.utcnow()

    def record_login(self) -> None:
        """Record successful login."""
        self.last_login_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def verify_account(self) -> None:
        """Mark account as verified."""
        self.is_verified = True
        self.updated_at = datetime.utcnow()

    def deactivate_account(self) -> None:
        """Deactivate user account."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate_account(self) -> None:
        """Activate user account."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def change_password(self, new_hashed_password: str) -> None:
        """Change user password."""
        self.hashed_password = new_hashed_password
        self.updated_at = datetime.utcnow()

    def can_login(self) -> bool:
        """Check if user can login."""
        return self.is_active and self.is_verified

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': str(self.id),
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
        }

    def to_public_dict(self) -> dict:
        """Convert to public dictionary (without sensitive info)."""
        return {
            'id': str(self.id),
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }