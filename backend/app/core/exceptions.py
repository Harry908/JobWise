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


# LLM Service Exceptions (Context7 pattern)
class LLMServiceError(HTTPException):
    """Base exception for LLM service errors."""

    def __init__(self, detail: str = "LLM service error", status_code: int = 500):
        super().__init__(status_code=status_code, detail=detail)


class RateLimitError(LLMServiceError):
    """Exception raised when LLM rate limit is exceeded."""

    def __init__(self, detail: str = "LLM rate limit exceeded"):
        super().__init__(detail=detail, status_code=429)


class LLMTimeoutError(LLMServiceError):
    """Exception raised when LLM request times out."""

    def __init__(self, detail: str = "LLM request timeout"):
        super().__init__(detail=detail, status_code=504)


class LLMValidationError(LLMServiceError):
    """Exception raised for invalid LLM parameters."""

    def __init__(self, detail: str = "Invalid LLM parameters"):
        super().__init__(detail=detail, status_code=422)


class DatabaseException(HTTPException):
    """Exception raised for database operation errors."""

    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(status_code=500, detail=detail)


class StorageException(HTTPException):
    """Exception raised for file storage errors."""

    def __init__(self, detail: str = "Storage operation failed"):
        super().__init__(status_code=500, detail=detail)


class TextExtractionError(HTTPException):
    """Exception raised for text extraction errors."""

    def __init__(self, detail: str = "Text extraction failed"):
        super().__init__(status_code=422, detail=detail)


class PreferenceExtractionException(HTTPException):
    """Exception raised for preference extraction errors."""

    def __init__(self, detail: str = "Preference extraction failed"):
        super().__init__(status_code=422, detail=detail)