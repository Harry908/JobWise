"""Security utilities for authentication and authorization."""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from .config import settings
from .exceptions import AuthenticationException, ValidationException


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTToken(BaseModel):
    """JWT token model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str


class TokenData(BaseModel):
    """Token payload data."""
    user_id: str
    exp: datetime
    iat: datetime
    type: str = "access"


class PasswordHasher:
    """Password hashing utilities using passlib/bcrypt."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        if not password:
            raise ValidationException("Password cannot be empty")

        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        if not password or not hashed_password:
            return False

        try:
            return pwd_context.verify(password, hashed_password)
        except Exception:
            return False


class JWTManager:
    """JWT token management utilities."""

    @staticmethod
    def create_access_token(
        user_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

        expire = datetime.utcnow() + expires_delta

        payload = TokenData(
            user_id=user_id,
            exp=expire,
            iat=datetime.utcnow(),
            type="access"
        )

        token = jwt.encode(
            payload.dict(),
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

        return token

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """Create a JWT refresh token."""
        expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

        payload = TokenData(
            user_id=user_id,
            exp=expire,
            iat=datetime.utcnow(),
            type="refresh"
        )

        token = jwt.encode(
            payload.dict(),
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

        return token

    @staticmethod
    def verify_token(token: str) -> TokenData:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            token_data = TokenData(**payload)

            # Check if token is expired
            if token_data.exp < datetime.utcnow():
                raise AuthenticationException("Token has expired")

            return token_data

        except JWTError as e:
            if "expired" in str(e).lower():
                raise AuthenticationException("Token has expired")
            else:
                raise AuthenticationException("Invalid token")
        except Exception as e:
            raise AuthenticationException(f"Token verification failed: {str(e)}")

    @staticmethod
    def get_user_id_from_token(token: str) -> str:
        """Extract user ID from JWT token."""
        token_data = JWTManager.verify_token(token)
        return token_data.user_id

    @staticmethod
    def is_token_expired(token: str) -> bool:
        """Check if a token is expired."""
        try:
            token_data = JWTManager.verify_token(token)
            return False
        except AuthenticationException:
            return True


class SecurityUtils:
    """General security utilities."""

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(length)

    @staticmethod
    def hash_string(value: str) -> str:
        """Create a SHA-256 hash of a string."""
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    @staticmethod
    def constant_time_compare(a: str, b: str) -> bool:
        """Constant time string comparison to prevent timing attacks."""
        return secrets.compare_digest(a, b)

    @staticmethod
    def sanitize_input(input_str: str, max_length: int = 1000) -> str:
        """Sanitize user input by trimming and limiting length."""
        if not input_str:
            return ""

        # Trim whitespace
        sanitized = input_str.strip()

        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized


# Convenience functions
def hash_password(password: str) -> str:
    """Hash a password."""
    return PasswordHasher.hash_password(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password."""
    return PasswordHasher.verify_password(password, hashed)


def create_access_token(user_id: str) -> str:
    """Create an access token."""
    return JWTManager.create_access_token(user_id)


def create_refresh_token(user_id: str) -> str:
    """Create a refresh token."""
    return JWTManager.create_refresh_token(user_id)


def verify_token(token: str) -> TokenData:
    """Verify a token."""
    return JWTManager.verify_token(token)


def get_user_id_from_token(token: str) -> str:
    """Get user ID from token."""
    return JWTManager.get_user_id_from_token(token)