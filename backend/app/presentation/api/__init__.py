"""
API Package Initialization

Centralized API router for all endpoints.
"""
from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

# Import and include sub-routers here as they are implemented
# Example:
# from .auth import router as auth_router
# from .profiles import router as profiles_router
# from .jobs import router as jobs_router
# from .generation import router as generation_router
# from .documents import router as documents_router

# api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
# api_router.include_router(profiles_router, prefix="/profiles", tags=["profiles"])
# api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
# api_router.include_router(generation_router, prefix="/generations", tags=["generation"])
# api_router.include_router(documents_router, prefix="/documents", tags=["documents"])

# Health check sub-router (can be moved to separate file later if needed)
health_router = APIRouter(tags=["health"])

@health_router.get("/ping")
async def ping():
    """Simple ping endpoint for connectivity testing."""
    return {"message": "pong"}

# Include health router
api_router.include_router(health_router, prefix="/health", tags=["health"])