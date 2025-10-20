"""
JobWise Backend Application Entry Point

FastAPI application with comprehensive middleware and error handling.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.exceptions import JobWiseException
from app.presentation.api import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager."""
    logger.info("Starting JobWise Backend...")

    # Startup logic
    logger.info("Application startup complete")

    yield

    # Shutdown logic
    logger.info("Shutting down JobWise Backend...")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered job application assistant backend",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url=None,  # disable separate Redoc route; redirect provided below
    lifespan=lifespan,
)

# Set up CORS
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add trusted host middleware (security)
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],  # Configure this properly in production
    )


# Global exception handlers
@app.exception_handler(JobWiseException)
async def jobwise_exception_handler(request: Request, exc: JobWiseException):
    """Handle custom JobWise exceptions."""
    logger.error(
        f"JobWise exception: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": str(request.url),
            "method": request.method,
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={
            "errors": exc.errors(),
            "path": str(request.url),
            "method": request.method,
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": exc.errors(),
            }
        },
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors from other contexts."""
    logger.warning(
        f"Pydantic validation error: {exc.errors()}",
        extra={
            "errors": exc.errors(),
            "path": str(request.url),
            "method": request.method,
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "validation_error",
                "message": "Data validation failed",
                "details": exc.errors(),
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.exception(
        f"Unexpected error: {str(exc)}",
        extra={
            "path": str(request.url),
            "method": request.method,
            "user_agent": request.headers.get("user-agent"),
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "An unexpected error occurred",
            }
        },
    )


# Include API routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Basic health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "health_check": "/health",
        "api_prefix": settings.API_V1_PREFIX,
    }


# Development-only endpoints
if settings.DEBUG:
    @app.get("/debug/config")
    async def debug_config():
        """Debug endpoint to check configuration (development only)."""
        return {
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "database_url": settings.DATABASE_URL.replace(settings.DATABASE_URL.split('@')[0].split('//')[1].split(':')[0], "***") if "@" in settings.DATABASE_URL else "configured",
            "redis_url": settings.REDIS_URL,
            "cors_origins": settings.CORS_ORIGINS,
            "api_prefix": settings.API_V1_PREFIX,
        }


# Note: Redoc route intentionally removed. Use /docs (Swagger UI) as the canonical API docs URL.