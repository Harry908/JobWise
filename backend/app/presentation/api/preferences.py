"""API endpoints for user preference management."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.preferences.writing_style_config import WritingStyleConfig
from app.domain.entities.preferences.layout_config import LayoutConfig
from app.domain.entities.preferences.user_generation_profile import UserGenerationProfile
from app.domain.entities.preferences.example_resume import ExampleResume
from app.infrastructure.repositories.writing_style_config_repository import WritingStyleConfigRepository
from app.infrastructure.repositories.layout_config_repository import LayoutConfigRepository
from app.infrastructure.repositories.user_generation_profile_repository import UserGenerationProfileRepository
from app.infrastructure.repositories.example_resume_repository import ExampleResumeRepository
from app.application.services.preference_extraction_service import PreferenceExtractionService
from app.application.services.file_upload.file_upload_service import FileUploadService
from app.application.services.file_upload.text_extraction_service import TextExtractionService
from app.infrastructure.adapters.groq_adapter import GroqAdapter
from app.infrastructure.database.connection import get_db_session
from app.core.dependencies import get_current_user
from app.core.exceptions import PreferenceExtractionException, ValidationException

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/preferences",
    tags=["preferences"],
    responses={404: {"description": "Not found"}}
)


# Dependency injection for services
def get_file_upload_service() -> FileUploadService:
    """Get file upload service instance."""
    return FileUploadService()


def get_text_extraction_service(db: AsyncSession = Depends(get_db_session)) -> TextExtractionService:
    """Get text extraction service instance."""
    return TextExtractionService(db)


def get_groq_adapter() -> GroqAdapter:
    """Get Groq adapter instance."""
    return GroqAdapter()


def get_preference_extraction_service(
    groq: GroqAdapter = Depends(get_groq_adapter),
    text_extractor: TextExtractionService = Depends(get_text_extraction_service)
) -> PreferenceExtractionService:
    """Get preference extraction service instance."""
    return PreferenceExtractionService(groq, text_extractor)


def get_writing_style_repo(db: AsyncSession = Depends(get_db_session)) -> WritingStyleConfigRepository:
    """Get writing style config repository."""
    return WritingStyleConfigRepository(db)


def get_layout_repo(db: AsyncSession = Depends(get_db_session)) -> LayoutConfigRepository:
    """Get layout config repository."""
    return LayoutConfigRepository(db)


def get_profile_repo(db: AsyncSession = Depends(get_db_session)) -> UserGenerationProfileRepository:
    """Get user generation profile repository."""
    return UserGenerationProfileRepository(db)


def get_example_resume_repo(db: AsyncSession = Depends(get_db_session)) -> ExampleResumeRepository:
    """Get example resume repository."""
    return ExampleResumeRepository(db)


@router.post("/upload-sample-resume")
async def upload_sample_resume(
    file: UploadFile = File(...),
    is_primary: bool = Form(default=False),
    current_user_id: int = Depends(get_current_user),
    file_service: FileUploadService = Depends(get_file_upload_service),
    extraction_service: PreferenceExtractionService = Depends(get_preference_extraction_service),
    layout_repo: LayoutConfigRepository = Depends(get_layout_repo),
    example_repo: ExampleResumeRepository = Depends(get_example_resume_repo),
    profile_repo: UserGenerationProfileRepository = Depends(get_profile_repo)
):
    """
    Upload sample resume and extract layout preferences.
    
    Args:
        file: Resume file (PDF, DOCX, or TXT)
        is_primary: Whether this should be the primary example resume
        current_user_id: Authenticated user ID
        
    Returns:
        Extraction result with layout preferences and example resume record
    """
    try:
        logger.info(f"User {current_user_id} uploading sample resume: {file.filename}")
        
        # Validate and save file
        save_result = await file_service.save_upload(
            file=file,
            user_id=current_user_id,
            category="example_resumes"
        )
        
        if not save_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=save_result.get("error", "File upload failed")
            )
        
        file_path = save_result["file_path"]
        
        # Extract layout preferences using LLM
        try:
            layout_config = await extraction_service.extract_layout_from_example_resume(
                file_path=file_path,
                user_id=current_user_id
            )
        except PreferenceExtractionException as e:
            logger.error(f"Layout extraction failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to extract layout preferences: {str(e)}"
            )
        
        # Save layout config to database
        saved_layout = await layout_repo.create(layout_config)
        
        # Create example resume record
        example_resume = ExampleResume(
            user_id=current_user_id,
            file_path=file_path,
            original_filename=file.filename,
            layout_config_id=saved_layout.id,
            is_primary=is_primary,
            file_hash=save_result.get("file_hash")
        )
        
        saved_example = await example_repo.create(example_resume)
        
        # If primary, update other resumes
        if is_primary:
            await example_repo.set_primary(saved_example.id, current_user_id)
        
        # Update or create user generation profile
        existing_profile = await profile_repo.get_by_user_id(current_user_id)
        
        if existing_profile:
            # Update existing profile with new layout config
            existing_profile.layout_config_id = saved_layout.id
            await profile_repo.update(existing_profile)
        
        return {
            "success": True,
            "message": "Sample resume uploaded and analyzed successfully",
            "example_resume_id": saved_example.id,
            "layout_config_id": saved_layout.id,
            "extraction_metadata": layout_config.extraction_metadata,
            "is_primary": is_primary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Upload sample resume failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process sample resume"
        )


@router.post("/upload-cover-letter")
async def upload_cover_letter(
    file: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user),
    file_service: FileUploadService = Depends(get_file_upload_service),
    extraction_service: PreferenceExtractionService = Depends(get_preference_extraction_service),
    style_repo: WritingStyleConfigRepository = Depends(get_writing_style_repo),
    profile_repo: UserGenerationProfileRepository = Depends(get_profile_repo)
):
    """
    Upload sample cover letter and extract writing style preferences.
    
    Args:
        file: Cover letter file (PDF, DOCX, or TXT)
        current_user_id: Authenticated user ID
        
    Returns:
        Extraction result with writing style preferences
    """
    try:
        logger.info(f"User {current_user_id} uploading sample cover letter: {file.filename}")
        
        # Validate and save file
        save_result = await file_service.save_upload(
            file=file,
            user_id=current_user_id,
            category="cover_letters"
        )
        
        if not save_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=save_result.get("error", "File upload failed")
            )
        
        file_path = save_result["file_path"]
        
        # Extract writing style using LLM
        try:
            writing_style = await extraction_service.extract_writing_style_from_cover_letter(
                file_path=file_path,
                user_id=current_user_id
            )
        except PreferenceExtractionException as e:
            logger.error(f"Writing style extraction failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to extract writing style: {str(e)}"
            )
        
        # Deactivate existing writing style configs
        existing_styles = await style_repo.get_by_user_id(current_user_id)
        for style in existing_styles:
            style.is_active = False
            await style_repo.update(style)
        
        # Save new writing style config
        saved_style = await style_repo.create(writing_style)
        
        # Update or create user generation profile
        existing_profile = await profile_repo.get_by_user_id(current_user_id)
        
        if existing_profile:
            # Update existing profile with new writing style
            existing_profile.writing_style_config_id = saved_style.id
            await profile_repo.update(existing_profile)
        
        return {
            "success": True,
            "message": "Cover letter uploaded and analyzed successfully",
            "writing_style_config_id": saved_style.id,
            "extraction_metadata": writing_style.extraction_metadata,
            "preferences": {
                "tone": writing_style.tone_preference,
                "formality": writing_style.formality_level,
                "sentence_structure": writing_style.sentence_structure,
                "vocabulary_complexity": writing_style.vocabulary_complexity
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Upload cover letter failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process cover letter"
        )


@router.get("/generation-profile")
async def get_generation_profile(
    current_user_id: int = Depends(get_current_user),
    profile_repo: UserGenerationProfileRepository = Depends(get_profile_repo)
):
    """
    Get user's generation profile with all preferences.
    
    Args:
        current_user_id: Authenticated user ID
        
    Returns:
        Complete generation profile with writing style and layout preferences
    """
    try:
        logger.info(f"Fetching generation profile for user {current_user_id}")
        
        profile = await profile_repo.get_by_user_id(current_user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generation profile not found. Please upload a cover letter and sample resume first."
            )
        
        return {
            "profile_id": profile.id,
            "user_id": profile.user_id,
            "writing_style": {
                "config_id": profile.writing_style_config_id,
                "tone": profile.writing_style_config.tone_preference if profile.writing_style_config else None,
                "formality": profile.writing_style_config.formality_level if profile.writing_style_config else None,
                "sentence_structure": profile.writing_style_config.sentence_structure if profile.writing_style_config else None
            } if profile.writing_style_config else None,
            "layout": {
                "config_id": profile.layout_config_id,
                "section_order": profile.layout_config.section_order_preference if profile.layout_config else None,
                "header_style": profile.layout_config.header_style if profile.layout_config else None
            } if profile.layout_config else None,
            "overall_quality_score": profile.overall_quality_score,
            "is_active": profile.is_active,
            "generation_preferences": profile.generation_preferences,
            "last_updated": profile.last_updated.isoformat() if profile.last_updated else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Get generation profile failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve generation profile"
        )


@router.put("/generation-profile")
async def update_generation_profile(
    generation_preferences: dict,
    current_user_id: int = Depends(get_current_user),
    profile_repo: UserGenerationProfileRepository = Depends(get_profile_repo)
):
    """
    Update user's generation preferences.
    
    Args:
        generation_preferences: Updated preference settings
        current_user_id: Authenticated user ID
        
    Returns:
        Updated profile
    """
    try:
        logger.info(f"Updating generation profile for user {current_user_id}")
        
        profile = await profile_repo.get_by_user_id(current_user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generation profile not found"
            )
        
        # Update preferences
        profile.generation_preferences = generation_preferences
        updated_profile = await profile_repo.update(profile)
        
        return {
            "success": True,
            "message": "Generation preferences updated successfully",
            "profile_id": updated_profile.id,
            "generation_preferences": updated_profile.generation_preferences
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Update generation profile failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update generation profile"
        )


@router.get("/example-resumes")
async def get_example_resumes(
    current_user_id: int = Depends(get_current_user),
    example_repo: ExampleResumeRepository = Depends(get_example_resume_repo)
):
    """
    Get all example resumes for current user.
    
    SECURITY: Only returns resumes belonging to authenticated user.
    
    Args:
        current_user_id: Authenticated user ID
        
    Returns:
        List of example resumes owned by the user
    """
    try:
        logger.info(f"Fetching example resumes for user {current_user_id}")
        
        # Repository filters by user_id automatically for security
        examples = await example_repo.get_by_user_id(current_user_id)
        
        return {
            "total": len(examples),
            "examples": [
                {
                    "id": str(ex.id),  # Ensure string format
                    "userId": ex.user_id,
                    "filePath": ex.file_path,
                    "originalFilename": ex.original_filename,
                    "layoutConfigId": str(ex.layout_config_id),
                    "isPrimary": ex.is_primary,
                    "fileHash": ex.file_hash,
                    "uploadedAt": ex.uploaded_at.isoformat() if ex.uploaded_at else None,
                    "fileSize": ex.file_size or 0,
                    "fileType": ex.file_type or "unknown"
                }
                for ex in examples
            ]
        }
        
    except Exception as e:
        logger.exception(f"Get example resumes failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve example resumes"
        )


@router.delete("/example-resumes/{resume_id}")
async def delete_example_resume(
    resume_id: int,
    current_user_id: int = Depends(get_current_user),
    example_repo: ExampleResumeRepository = Depends(get_example_resume_repo),
    file_service: FileUploadService = Depends(get_file_upload_service)
):
    """
    Delete an example resume.
    
    SECURITY: Verifies user owns the resume before deletion.
    
    Args:
        resume_id: Example resume ID
        current_user_id: Authenticated user ID
        
    Returns:
        Deletion confirmation
    """
    try:
        logger.info(f"Deleting example resume {resume_id} for user {current_user_id}")
        
        example = await example_repo.get_by_id(resume_id)
        
        if not example:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Example resume not found"
            )
        
        # SECURITY CHECK: Verify ownership
        if example.user_id != current_user_id:
            logger.warning(f"Unauthorized delete attempt: user {current_user_id} tried to delete resume {resume_id} owned by user {example.user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this resume"
            )
        
        # Verify file ownership as additional security layer
        if hasattr(example, 'file_path') and example.file_path:
            if not file_service.verify_file_ownership(example.file_path, current_user_id):
                logger.error(f"File ownership verification failed for resume {resume_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="File ownership verification failed"
                )
        
        success = await example_repo.delete(resume_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete example resume"
            )
        
        return {
            "success": True,
            "message": "Example resume deleted successfully",
            "resume_id": resume_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Delete example resume failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete example resume"
        )


@router.post("/example-resumes/{resume_id}/set-primary")
async def set_primary_example(
    resume_id: int,
    current_user_id: int = Depends(get_current_user),
    example_repo: ExampleResumeRepository = Depends(get_example_resume_repo)
):
    """
    Set an example resume as primary.
    
    SECURITY: Verifies user owns the resume before modification.
    
    Args:
        resume_id: Example resume ID
        current_user_id: Authenticated user ID
        
    Returns:
        Update confirmation
    """
    try:
        logger.info(f"Setting example resume {resume_id} as primary for user {current_user_id}")
        
        example = await example_repo.get_by_id(resume_id)
        
        if not example:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Example resume not found"
            )
        
        # SECURITY CHECK: Verify ownership
        if example.user_id != current_user_id:
            logger.warning(f"Unauthorized primary set attempt: user {current_user_id} tried to modify resume {resume_id} owned by user {example.user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this resume"
            )
        
        # Set as primary (repository method ensures only one primary per user)
        await example_repo.set_primary(resume_id, current_user_id)
        
        return {
            "success": True,
            "message": "Example resume set as primary",
            "resume_id": resume_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Set primary example failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set primary example"
        )
