"""
API Package Initialization

Centralized API router for all endpoints.
"""
from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

# Import and include sub-routers here as they are implemented
from .auth import router as auth_router
from .jobs import router as jobs_router
from .job_descriptions import router as job_descriptions_router
from .profiles import router as profiles_router

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
api_router.include_router(job_descriptions_router)  # Prefix defined in router
api_router.include_router(profiles_router, prefix="/profiles", tags=["profiles"])
# api_router.include_router(generation_router, prefix="/generations", tags=["generation"])
# api_router.include_router(documents_router, prefix="/documents", tags=["documents"])

# Health check sub-router (can be moved to separate file later if needed)
health_router = APIRouter(tags=["health"])

@health_router.get("/ping")
async def ping():
    """Simple ping endpoint for connectivity testing."""
    return {"message": "pong"}

@health_router.get("/health")
async def health_check():
    """Comprehensive health check including database connectivity."""
    from app.infrastructure.database.connection import check_database_health, get_database_info
    from app.core.config import get_settings

    settings = get_settings()

    # Check database health
    db_healthy = await check_database_health()
    db_info = await get_database_info() if db_healthy else {"status": "unhealthy"}

    # Overall health status
    overall_healthy = db_healthy

    health_status = {
        "status": "healthy" if overall_healthy else "unhealthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "timestamp": "2024-01-15T10:00:00Z",  # Would use datetime.utcnow() in real implementation
        "checks": {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "details": db_info
            }
        }
    }

    return health_status

# Include health router
api_router.include_router(health_router, prefix="/health", tags=["health"])