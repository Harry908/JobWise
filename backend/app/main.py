"""
JobWise Backend Application Entry Point

Simplified FastAPI application for development setup.
"""
from fastapi import FastAPI

# Create FastAPI application
app = FastAPI(
    title="JobWise API",
    description="AI-powered job application assistant backend",
    version="1.0.0",
)

# Basic health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "JobWise Backend",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "name": "JobWise API",
        "version": "1.0.0",
        "status": "operational",
        "docs_url": "/docs",
        "health_check": "/health",
    }