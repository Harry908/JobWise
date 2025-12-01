"""Sample document API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.dependencies import get_db_session, get_current_user
from app.infrastructure.repositories.sample_repository import SampleRepository
from app.application.services.sample_service import SampleService


router = APIRouter(prefix="/samples", tags=["samples"])


# Response schemas
class SampleResponse(BaseModel):
    """Sample response without full text."""
    id: str
    user_id: int
    document_type: str
    original_filename: str
    word_count: int
    character_count: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SampleDetailResponse(SampleResponse):
    """Sample response with full text and writing style."""
    full_text: str
    writing_style: Optional[dict] = None
    updated_at: datetime


class SampleListResponse(BaseModel):
    """Response for listing samples."""
    samples: list[SampleResponse]
    total: int


async def get_sample_repository(db: AsyncSession = Depends(get_db_session)) -> SampleRepository:
    """Dependency to get sample repository."""
    return SampleRepository(db)


async def get_sample_service(repo: SampleRepository = Depends(get_sample_repository)) -> SampleService:
    """Dependency to get sample service."""
    return SampleService(repo)


@router.post("/upload", response_model=SampleResponse, status_code=status.HTTP_201_CREATED)
async def upload_sample(
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: int = Depends(get_current_user),
    service: SampleService = Depends(get_sample_service)
):
    """
    Upload a sample document for writing style extraction.
    
    Accepts .txt files only (max 1MB).
    Automatically deactivates previous samples of the same type.
    """
    sample = await service.upload_sample(
        user_id=current_user,
        document_type=document_type,
        file=file
    )
    
    return SampleResponse(
        id=sample.id,
        user_id=sample.user_id,
        document_type=sample.document_type,
        original_filename=sample.original_filename,
        word_count=sample.word_count,
        character_count=sample.character_count,
        is_active=sample.is_active,
        created_at=sample.created_at
    )


@router.get("", response_model=SampleListResponse)
async def list_samples(
    document_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: int = Depends(get_current_user),
    service: SampleService = Depends(get_sample_service)
):
    """
    List all sample documents for the authenticated user.
    
    Optional filters:
    - document_type: Filter by 'resume' or 'cover_letter'
    - is_active: Filter by active status
    """
    samples = await service.list_samples(
        user_id=current_user,
        document_type=document_type,
        is_active=is_active
    )
    
    return SampleListResponse(
        samples=[
            SampleResponse(
                id=s.id,
                user_id=s.user_id,
                document_type=s.document_type,
                original_filename=s.original_filename,
                word_count=s.word_count,
                character_count=s.character_count,
                is_active=s.is_active,
                created_at=s.created_at
            )
            for s in samples
        ],
        total=len(samples)
    )


@router.get("/{sample_id}", response_model=SampleDetailResponse)
async def get_sample(
    sample_id: str,
    current_user: int = Depends(get_current_user),
    service: SampleService = Depends(get_sample_service)
):
    """
    Get detailed information about a specific sample document.
    
    Returns full text and writing style analysis (if available).
    """
    sample = await service.get_sample(sample_id, current_user)
    
    return SampleDetailResponse(
        id=sample.id,
        user_id=sample.user_id,
        document_type=sample.document_type,
        original_filename=sample.original_filename,
        full_text=sample.full_text,
        writing_style=sample.writing_style,
        word_count=sample.word_count,
        character_count=sample.character_count,
        is_active=sample.is_active,
        created_at=sample.created_at,
        updated_at=sample.updated_at
    )


@router.delete("/{sample_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sample(
    sample_id: str,
    current_user: int = Depends(get_current_user),
    service: SampleService = Depends(get_sample_service)
):
    """
    Delete a sample document permanently.
    """
    await service.delete_sample(sample_id, current_user)
    return None
