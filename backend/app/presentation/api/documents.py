# Document Management API Router

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session, get_current_user
from app.domain.entities.user import User
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def list_documents(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """List user's documents with pagination and filtering."""
    try:
        # Mock implementation
        return {
            "documents": [
                {
                    "id": "doc-uuid-1",
                    "filename": "resume_senior_python_developer.pdf",
                    "document_type": "resume",
                    "file_size": 245760,
                    "created_at": "2025-10-21T10:30:05Z",
                    "download_url": "/api/v1/documents/doc-uuid-1/download"
                }
            ],
            "pagination": {
                "total": 1,
                "limit": limit,
                "offset": offset,
                "has_next": False,
                "has_previous": False
            }
        }
    except Exception as e:
        logger.exception("Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """Get document details by ID."""
    try:
        # Mock implementation
        return {
            "id": document_id,
            "filename": "resume_senior_python_developer.pdf",
            "document_type": "resume",
            "file_size": 245760,
            "ats_score": 0.87,
            "created_at": "2025-10-21T10:30:05Z",
            "download_url": f"/api/v1/documents/{document_id}/download",
            "generation_id": "gen-uuid-1",
            "metadata": {
                "template": "modern",
                "pages": 1,
                "keywords_matched": 15
            }
        }
    except Exception as e:
        logger.exception(f"Failed to get document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Download document PDF file."""
    try:
        # Mock implementation - return a simple text response
        # In real implementation, this would return FileResponse with actual PDF
        return {
            "message": f"Download for document {document_id} would be implemented here",
            "document_id": document_id,
            "content_type": "application/pdf",
            "filename": "resume_senior_python_developer.pdf"
        }
    except Exception as e:
        logger.exception(f"Failed to download document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{document_id}/share")
async def create_share_link(
    document_id: str,
    expires_in_days: int = Query(7, ge=1, le=30, description="Link expiration in days"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """Create a shareable link for the document."""
    try:
        # Mock implementation
        return {
            "share_id": f"share-{document_id}",
            "share_url": f"/api/v1/documents/shared/{document_id}?token=share-token",
            "expires_at": "2025-10-28T10:30:05Z",
            "document_id": document_id
        }
    except Exception as e:
        logger.exception(f"Failed to create share link for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """Delete a document."""
    try:
        # Mock implementation
        return {"message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        logger.exception(f"Failed to delete document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/shared/{document_id}")
async def access_shared_document(
    document_id: str,
    token: str = Query(..., description="Share token"),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """Access a shared document (public endpoint)."""
    try:
        # Mock implementation - in real implementation, validate token
        return {
            "document_id": document_id,
            "filename": "resume_senior_python_developer.pdf",
            "document_type": "resume",
            "download_url": f"/api/v1/documents/{document_id}/download?token={token}",
            "shared_at": "2025-10-21T10:30:05Z",
            "expires_at": "2025-10-28T10:30:05Z"
        }
    except Exception as e:
        logger.exception(f"Failed to access shared document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")