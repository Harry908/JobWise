from typing import Optional, Dict, Any
from fastapi import HTTPException


class AuthenticationException(HTTPException):
    """Exception raised for authentication errors."""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=401, detail=detail)


class ValidationException(HTTPException):
    """Exception raised for validation errors."""

    def __init__(
        self,
        detail: str = "Validation failed",
        error_code: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=400, detail=detail)
        self.error_code = error_code
        self.message = message or detail
        self.details = details or {}


class NotFoundError(HTTPException):
    """Exception raised when resource is not found."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)


class ForbiddenException(HTTPException):
    """Exception raised for forbidden access."""

    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(status_code=403, detail=detail)


class ConflictException(HTTPException):
    """Exception raised when resource already exists or conflicts with existing data."""

    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=409, detail=detail)


class DatabaseException(HTTPException):
    """Exception raised for database operation errors."""

    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(status_code=500, detail=detail)


class StorageException(HTTPException):
    """Exception raised for file storage errors."""

    def __init__(self, detail: str = "Storage operation failed"):
        super().__init__(status_code=500, detail=detail)


