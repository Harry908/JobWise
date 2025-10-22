"""Custom exceptions for the application."""

from fastapi import HTTPException


class AuthenticationException(HTTPException):
    """Exception raised for authentication errors."""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=401, detail=detail)


class ValidationException(HTTPException):
    """Exception raised for validation errors."""

    def __init__(self, detail: str = "Validation failed"):
        super().__init__(status_code=400, detail=detail)


class NotFoundError(HTTPException):
    """Exception raised when resource is not found."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)


class ForbiddenException(HTTPException):
    """Exception raised for forbidden access."""

    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(status_code=403, detail=detail)