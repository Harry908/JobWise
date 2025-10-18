"""Custom exception classes for JobWise application."""

from typing import Any, Dict, Optional


class JobWiseException(Exception):
    """Base exception class for JobWise application."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(JobWiseException):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="validation_error",
            status_code=400,
            details=details,
        )


class AuthenticationException(JobWiseException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="authentication_error",
            status_code=401,
        )


class AuthorizationException(JobWiseException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_code="authorization_error",
            status_code=403,
        )


class NotFoundError(JobWiseException):
    """Raised when a resource is not found."""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            error_code="not_found",
            status_code=404,
            details={"resource": resource, "identifier": identifier},
        )


class ConflictError(JobWiseException):
    """Raised when a resource conflict occurs."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="conflict",
            status_code=409,
            details=details,
        )


class RateLimitExceeded(JobWiseException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, retry_after: int):
        super().__init__(
            message="Rate limit exceeded",
            error_code="rate_limit_exceeded",
            status_code=429,
            details={"retry_after": retry_after},
        )


class ExternalServiceError(JobWiseException):
    """Raised when external service call fails."""
    
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"{service} service error: {message}",
            error_code="external_service_error",
            status_code=502,
            details={"service": service},
        )


class AIGenerationError(JobWiseException):
    """Raised when AI generation fails."""
    
    def __init__(self, stage: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"AI generation failed at {stage}: {message}",
            error_code="ai_generation_error",
            status_code=500,
            details={**(details or {}), "stage": stage},
        )


class TokenBudgetExceeded(JobWiseException):
    """Raised when token budget is exceeded."""
    
    def __init__(self, used: int, limit: int):
        super().__init__(
            message=f"Token budget exceeded: {used}/{limit}",
            error_code="token_budget_exceeded",
            status_code=400,
            details={"tokens_used": used, "token_limit": limit},
        )


class PDFGenerationError(JobWiseException):
    """Raised when PDF generation fails."""
    
    def __init__(self, message: str):
        super().__init__(
            message=f"PDF generation failed: {message}",
            error_code="pdf_generation_error",
            status_code=500,
        )


class DatabaseError(JobWiseException):
    """Raised when database operation fails."""
    
    def __init__(self, operation: str, message: str):
        super().__init__(
            message=f"Database {operation} failed: {message}",
            error_code="database_error",
            status_code=500,
            details={"operation": operation},
        )