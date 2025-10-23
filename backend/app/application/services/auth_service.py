"""Authentication service for user management and JWT handling."""

from datetime import datetime
from typing import Optional

from app.core.exceptions import AuthenticationException, ValidationException, NotFoundError
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_user_id_from_token
)
from app.domain.entities.user import User
from app.infrastructure.repositories.user_repository import UserRepository


class AuthService:
    """Authentication service handling user registration, login, and token management."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register_user(self, email: str, password: str, full_name: str) -> dict:
        """Register a new user."""
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise ValidationException("User with this email already exists")

        # Validate email format
        if not User.validate_email(email):
            raise ValidationException("Invalid email format")

        # Validate password strength
        if not User.validate_password(password):
            raise ValidationException(
                "Password must be at least 8 characters long and contain "
                "uppercase, lowercase, and numeric characters"
            )

        # Hash password
        password_hash = hash_password(password)

        # Create user
        user = User(
            id=None,
            email=email,
            password_hash=password_hash,
            full_name=full_name
        )

        created_user = await self.user_repository.create(user)

        # Generate tokens
        access_token = create_access_token({"sub": str(created_user.id)})
        refresh_token = create_refresh_token({"sub": str(created_user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": {
                "id": created_user.id,
                "email": created_user.email,
                "full_name": created_user.full_name,
                "created_at": created_user.created_at.isoformat() if created_user.created_at else None
            }
        }

    async def login_user(self, email: str, password: str) -> dict:
        """Authenticate user and return tokens."""
        # Get user by email
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise AuthenticationException("Invalid credentials")

        # Verify password
        if not verify_password(password, user.password_hash):
            raise AuthenticationException("Invalid credentials")

        # Check if user is active
        if not user.is_active:
            raise AuthenticationException("Account is deactivated")

        # Generate tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        }

    async def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token."""
        # Verify refresh token
        user_id = get_user_id_from_token(refresh_token)
        if not user_id:
            raise AuthenticationException("Invalid refresh token")

        # Get user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise AuthenticationException("User not found")

        # Check if user is active
        if not user.is_active:
            raise AuthenticationException("Account is deactivated")

        # Generate new tokens
        import time
        time.sleep(0.001)  # Small delay to ensure different timestamps
        access_token = create_access_token({"sub": str(user.id)})
        new_refresh_token = create_refresh_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        }

    async def get_current_user(self, user_id: int) -> dict:
        """Get current user profile."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }

    async def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        """Change user's password."""
        # Get user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise AuthenticationException("Current password is incorrect")

        # Validate new password strength
        if not User.validate_password(new_password):
            raise ValidationException(
                "Password must be at least 8 characters long and contain "
                "uppercase, lowercase, and numeric characters"
            )

        # Check if new password is different from current
        if verify_password(new_password, user.password_hash):
            raise ValidationException("New password must be different from current password")

        # Hash new password
        new_password_hash = hash_password(new_password)

        # Update user password
        user.password_hash = new_password_hash
        user.updated_at = datetime.utcnow()
        await self.user_repository.update(user)

    async def forgot_password(self, email: str) -> None:
        """Request password reset (mock implementation)."""
        # Validate email format
        if not User.validate_email(email):
            raise ValidationException("Invalid email format")

        # In a real implementation, this would:
        # 1. Check if user exists
        # 2. Generate a reset token
        # 3. Store token with expiry
        # 4. Send email with reset link
        # For now, we'll just validate the email format
        pass

    async def reset_password(self, token: str, new_password: str) -> None:
        """Reset password with token (mock implementation)."""
        # Validate new password strength
        if not User.validate_password(new_password):
            raise ValidationException(
                "Password must be at least 8 characters long and contain "
                "uppercase, lowercase, and numeric characters"
            )

        # In a real implementation, this would:
        # 1. Validate reset token
        # 2. Check token expiry
        # 3. Find user by token
        # 4. Update password
        # 5. Invalidate token
        # For now, we'll just validate the password and accept any token
        if not token or len(token) < 10:
            raise ValidationException("Invalid reset token")

    async def check_email_availability(self, email: str) -> dict:
        """Check if an email is available for registration."""
        # Validate email format
        if not User.validate_email(email):
            raise ValidationException("Invalid email format")

        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(email)
        available = existing_user is None

        return {"available": available}