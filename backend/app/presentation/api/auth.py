"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from app.application.services.auth_service import AuthService
from app.core.dependencies import get_auth_service, get_current_user
from app.core.exceptions import AuthenticationException, ValidationException
from app.core.security import get_user_id_from_token


# Request/Response models
class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
                "full_name": "John Doe"
            }
        }
    }


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }
    }


class RefreshTokenRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str = Field(..., description="Refresh token")

    model_config = {
        "json_schema_extra": {
            "example": {
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        }
    }


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    user: dict


class UserProfile(BaseModel):
    """User profile response."""
    id: int
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: Optional[str]
    updated_at: Optional[str]


class ChangePasswordRequest(BaseModel):
    """Change password request."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    model_config = {
        "json_schema_extra": {
            "example": {
                "current_password": "CurrentPass123!",
                "new_password": "NewSecurePass456!"
            }
        }
    }


class ForgotPasswordRequest(BaseModel):
    """Forgot password request."""
    email: EmailStr = Field(..., description="User email address")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com"
            }
        }
    }


class ResetPasswordRequest(BaseModel):
    """Reset password request."""
    token: str = Field(..., description="Reset token from email")
    new_password: str = Field(..., min_length=8, description="New password")

    model_config = {
        "json_schema_extra": {
            "example": {
                "token": "reset_token_from_email",
                "new_password": "NewSecurePass456!"
            }
        }
    }


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


# Router
router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register_user(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user account."""
    try:
        return await auth_service.register_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", response_model=TokenResponse)
async def login_user(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate user and return access tokens."""
    try:
        return await auth_service.login_user(
            email=request.email,
            password=request.password
        )
    except AuthenticationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token using refresh token."""
    try:
        return await auth_service.refresh_access_token(request.refresh_token)
    except AuthenticationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user_id: int = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get current user profile information."""
    try:
        return await auth_service.get_current_user(current_user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/logout")
async def logout_user(
    current_user_id: int = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Logout user by invalidating their session."""
    try:
        # In a stateless JWT system, logout is typically handled client-side
        # by removing tokens. Server-side we could implement token blacklisting
        # but for now, we'll just return success
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user_id: int = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Change current user's password."""
    try:
        await auth_service.change_password(
            user_id=current_user_id,
            current_password=request.current_password,
            new_password=request.new_password
        )
        return {"message": "Password changed successfully"}
    except AuthenticationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Request password reset (mock implementation)."""
    try:
        # Mock implementation - in real app, this would send email
        await auth_service.forgot_password(request.email)
        return {"message": "If the email exists, a reset link has been sent"}
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reset password with token (mock implementation)."""
    try:
        # Mock implementation - in real app, this would validate token
        await auth_service.reset_password(
            token=request.token,
            new_password=request.new_password
        )
        return {"message": "Password reset successfully"}
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except AuthenticationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")