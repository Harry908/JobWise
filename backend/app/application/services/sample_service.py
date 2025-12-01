"""Sample document service for business logic."""

from typing import List, Optional
from fastapi import UploadFile, HTTPException, status

from app.domain.entities.sample import Sample
from app.infrastructure.repositories.sample_repository import SampleRepository


class SampleService:
    """Service for sample document business logic."""

    MAX_FILE_SIZE = 1024 * 1024  # 1 MB in bytes

    def __init__(self, repository: SampleRepository):
        """Initialize service with repository."""
        self.repository = repository

    async def upload_sample(
        self,
        user_id: int,
        document_type: str,
        file: UploadFile
    ) -> Sample:
        """
        Upload and process a sample document.
        
        Validates file type, size, and content.
        Automatically deactivates previous samples of the same type.
        """
        # Validate document type
        if document_type not in ["resume", "cover_letter"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="document_type must be 'resume' or 'cover_letter'"
            )

        # Validate file extension
        if not file.filename or not file.filename.endswith('.txt'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only .txt files are supported in this prototype"
            )

        # Read file content
        try:
            content = await file.read()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read file: {str(e)}"
            )

        # Validate file size
        if len(content) > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 1MB limit"
            )

        # Decode content as UTF-8
        try:
            full_text = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be UTF-8 encoded"
            )

        # Validate content is not empty
        if not full_text or not full_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="File is empty or contains no readable text"
            )

        # Calculate metrics
        word_count = len(full_text.split())
        character_count = len(full_text)

        # Create sample entity
        sample = Sample(
            user_id=user_id,
            document_type=document_type,
            original_filename=file.filename,
            full_text=full_text,
            word_count=word_count,
            character_count=character_count,
            is_active=True
        )

        # Save to database (repository handles deactivation of old samples)
        return await self.repository.create(sample)

    async def get_sample(self, sample_id: str, user_id: int) -> Sample:
        """Get sample by ID (scoped to user)."""
        sample = await self.repository.get_by_id(sample_id, user_id)
        if not sample:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sample document not found"
            )
        return sample

    async def list_samples(
        self,
        user_id: int,
        document_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Sample]:
        """List all samples for a user with optional filters."""
        if document_type and document_type not in ["resume", "cover_letter"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="document_type must be 'resume' or 'cover_letter'"
            )
        
        return await self.repository.list_by_user(user_id, document_type, is_active)

    async def delete_sample(self, sample_id: str, user_id: int) -> None:
        """Delete a sample document."""
        deleted = await self.repository.delete(sample_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sample document not found"
            )

    async def get_active_sample(self, user_id: int, document_type: str) -> Optional[Sample]:
        """Get the active sample for a user and document type."""
        if document_type not in ["resume", "cover_letter"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="document_type must be 'resume' or 'cover_letter'"
            )
        
        return await self.repository.get_active_sample(user_id, document_type)
