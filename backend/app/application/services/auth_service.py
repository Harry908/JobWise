"""Authentication service for user management and JWT handling."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from ...core.exceptions import AuthenticationException, ValidationException, NotFoundError
from ...core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_user_id_from_token
)
from ...domain.entities.user import User
from ...infrastructure.database.repositories import UserRepository
from ..dtos.auth_dtos import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    PasswordChangeRequest
)


class AuthService:
    """Authentication service handling user registration, login, and token management."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register_user(self, request: UserRegisterRequest) -> UserResponse:
        """Register a new user."""
        try:
            # Check if user already exists
            existing_user = await self.user_repository.get_by_email(request.email)
            if existing_user:
                raise ValidationException("User with this email already exists")

            # Validate email format (additional validation beyond Pydantic)
            if not User.validate_email(request.email):
                raise ValidationException("Invalid email format")

            # Validate password strength (additional validation beyond Pydantic)
            if not User.validate_password(request.password):
                raise ValidationException(
                    "Password must be at least 8 characters long and contain "
                    "uppercase, lowercase, and numeric characters"
                )

            # Truncate password to 72 bytes before hashing
            truncated_password = request.password[:72]

            # Hash password
            hashed_password = hash_password(truncated_password)

            # Create user data
            user_data = {
                "email": request.email,
                "password_hash": hashed_password,
                "first_name": request.full_name.split()[0] if request.full_name.split() else "",
                "last_name": " ".join(request.full_name.split()[1:]) if len(request.full_name.split()) > 1 else "",
                "is_active": True,
                "is_verified": True  # For testing - in production this would be False until email verification
            }

            # Create user in database
            user_model = await self.user_repository.create(user_data)

            # Convert to domain entity
            user = User(
                id=UUID(user_model.id),
                email=user_model.email,
                hashed_password=user_model.password_hash,
                full_name=request.full_name,
                is_active=user_model.is_active,
                is_verified=user_model.is_verified,
                created_at=user_model.created_at,
                updated_at=user_model.updated_at,
                last_login_at=user_model.last_active_at
            )

            # Log successful user creation
            print("User successfully created:", user)

            return UserResponse(
                id=str(user.id),
                email=user.email,
                full_name=user.full_name,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login_at=user.last_login_at
            )
        except Exception as e:
            # Log unexpected errors
            print("Error during user registration:", str(e))
            raise

    async def authenticate_user(self, request: UserLoginRequest) -> TokenResponse:
        """Authenticate user and return tokens."""
        # Get user by email
        user_model = await self.user_repository.get_by_email(request.email)
        if not user_model:
            raise AuthenticationException("Invalid email or password")

        # Convert to domain entity for validation
        user = User(
            id=UUID(user_model.id),
            email=user_model.email,
            hashed_password=user_model.password_hash,
            full_name=f"{user_model.first_name} {user_model.last_name}".strip(),
            is_active=user_model.is_active,
            is_verified=user_model.is_verified,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
            last_login_at=user_model.last_active_at
        )

        # Check if user can login
        if not user.can_login():
            if not user.is_active:
                raise AuthenticationException("Account is deactivated")
            if not user.is_verified:
                raise AuthenticationException("Account is not verified")
            raise AuthenticationException("Login not allowed")

        # Verify password (truncate to 72 bytes to match registration)
        truncated_password = request.password[:72]
        if not verify_password(truncated_password, user.hashed_password):
            raise AuthenticationException("Invalid email or password")

        # Update last login
        await self.user_repository.update_last_login(str(user.id))

        # Generate tokens
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1800,  # 30 minutes
            user_id=str(user.id)
        )

    async def refresh_access_token(self, request: RefreshTokenRequest) -> TokenResponse:
        """Refresh access token using refresh token."""
        try:
            # Verify refresh token
            user_id = get_user_id_from_token(request.refresh_token)

            # Get user to ensure they still exist and are active
            user_model = await self.user_repository.get_by_id(user_id)
            if not user_model or not user_model.is_active:
                raise AuthenticationException("Invalid refresh token")

            # Generate new tokens
            access_token = create_access_token(user_id)
            refresh_token = create_refresh_token(user_id)

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=1800,  # 30 minutes
                user_id=user_id
            )

        except Exception:
            raise AuthenticationException("Invalid refresh token")

    async def get_current_user(self, user_id: str) -> UserResponse:
        """Get current user information."""
        user_model = await self.user_repository.get_by_id(user_id)
        if not user_model:
            raise NotFoundError("User", user_id)

        return UserResponse(
            id=user_model.id,
            email=user_model.email,
            full_name=f"{user_model.first_name} {user_model.last_name}".strip(),
            is_active=user_model.is_active,
            is_verified=user_model.is_verified,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
            last_login_at=user_model.last_active_at
        )

    async def change_password(self, user_id: str, request: PasswordChangeRequest) -> None:
        """Change user password."""
        # Get user
        user_model = await self.user_repository.get_by_id(user_id)
        if not user_model:
            raise NotFoundError("User", user_id)

        # Convert to domain entity for password verification
        user = User(
            id=UUID(user_model.id),
            email=user_model.email,
            hashed_password=user_model.password_hash,
            full_name=f"{user_model.first_name} {user_model.last_name}".strip(),
            is_active=user_model.is_active,
            is_verified=user_model.is_verified,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
            last_login_at=user_model.last_active_at
        )

        # Verify current password
        if not verify_password(request.current_password, user.hashed_password):
            raise AuthenticationException("Current password is incorrect")

        # Validate new password
        if not User.validate_password(request.new_password):
            raise ValidationException(
                "New password must be at least 8 characters long and contain "
                "uppercase, lowercase, and numeric characters"
            )

        # Hash new password
        new_hashed_password = hash_password(request.new_password)

        # Update password
        await self.user_repository.update(user_id, {"password_hash": new_hashed_password})

    async def verify_user_account(self, user_id: str) -> None:
        """Verify user account."""
        user_model = await self.user_repository.get_by_id(user_id)
        if not user_model:
            raise NotFoundError("User", user_id)

        if user_model.is_verified:
            raise ValidationException("Account is already verified")

        await self.user_repository.update(user_id, {"is_verified": True})

    async def deactivate_user_account(self, user_id: str) -> None:
        """Deactivate user account."""
        user_model = await self.user_repository.get_by_id(user_id)
        if not user_model:
            raise NotFoundError("User", user_id)

        await self.user_repository.update(user_id, {"is_active": False})

    async def activate_user_account(self, user_id: str) -> None:
        """Activate user account."""
        user_model = await self.user_repository.get_by_id(user_id)
        if not user_model:
            raise NotFoundError("User", user_id)

        await self.user_repository.update(user_id, {"is_active": True})