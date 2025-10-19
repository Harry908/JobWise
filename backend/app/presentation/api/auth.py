"""Authentication API endpoints."""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.services.auth_service import AuthService
from ...infrastructure.database.connection import get_database_session_dependency
from ...infrastructure.database.repositories import RepositoryFactory
from ...presentation.middleware.auth import get_current_user_id
from ...application.dtos.auth_dtos import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    PasswordChangeRequest,
    EmailVerificationRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest
)
from ...core.exceptions import ValidationException

# Create auth router
router = APIRouter()


def get_auth_service(session: AsyncSession = Depends(get_database_session_dependency)) -> AuthService:
    """Dependency to get auth service."""
    user_repo = RepositoryFactory(session).create_user_repository()
    return AuthService(user_repo)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password."
)
async def register_user(
    request: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    """Register a new user."""
    try:
        return await auth_service.register_user(request)
    except ValidationException as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and return JWT tokens."
)
async def login_user(
    request: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """Authenticate user and return tokens."""
    try:
        return await auth_service.authenticate_user(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Refresh access token using refresh token."
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """Refresh access token."""
    try:
        return await auth_service.refresh_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get information about the currently authenticated user."
)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    """Get current user information."""
    try:
        return await auth_service.get_current_user(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put(
    "/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change password",
    description="Change the current user's password."
)
async def change_password(
    request: PasswordChangeRequest,
    user_id: str = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service)
) -> None:
    """Change user password."""
    try:
        await auth_service.change_password(user_id, request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/verify-email",
    status_code=status.HTTP_200_OK,
    summary="Request email verification",
    description="Request email verification for account activation."
)
async def request_email_verification(
    request: EmailVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """Request email verification."""
    # For now, just return success
    # In a real implementation, this would send an email
    return {"message": "Verification email sent"}


@router.post(
    "/verify-email/{token}",
    status_code=status.HTTP_200_OK,
    summary="Verify email",
    description="Verify user email using verification token."
)
async def verify_email(
    token: str,
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """Verify user email."""
    try:
        # In a real implementation, decode the token to get user_id
        # For now, this is a placeholder
        user_id = "placeholder_user_id"
        await auth_service.verify_user_account(user_id)
        return {"message": "Email verified successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Request password reset email."
)
async def request_password_reset(
    request: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """Request password reset."""
    # For now, just return success
    # In a real implementation, this would send an email
    return {"message": "Password reset email sent"}


@router.post(
    "/reset-password/confirm",
    status_code=status.HTTP_200_OK,
    summary="Confirm password reset",
    description="Reset password using reset token."
)
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """Confirm password reset."""
    try:
        # In a real implementation, decode the token to get user_id
        # For now, this is a placeholder
        user_id = "placeholder_user_id"
        await auth_service.change_password(user_id, PasswordChangeRequest(
            current_password="old_password",  # Not used in reset flow
            new_password=request.new_password
        ))
        return {"message": "Password reset successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout the current user (client should discard tokens)."
)
async def logout_user() -> dict:
    """Logout user."""
    # In a stateless JWT system, logout is handled client-side
    # by discarding the tokens. In a real implementation with
    # token blacklisting, this would invalidate the tokens.
    return {"message": "Logged out successfully"}