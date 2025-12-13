"""
Export API Router
Endpoints for document export (PDF/DOCX/ZIP).
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pathlib import Path
import hashlib
from datetime import datetime

from app.domain.enums.export_format import ExportFormat
from app.domain.enums.template_type import TemplateType
from app.presentation.schemas.export import (
    ExportRequest,
    ExportResponse,
    BatchExportRequest,
    BatchExportResponse,
    TemplateInfo,
    TemplateListResponse,
    ExportedFileListResponse,
    JobExportsResponse
)
from app.application.services.export_service import ExportService
from app.application.services.export_renderer import ExportRenderer
from app.infrastructure.storage.s3_storage_adapter import S3StorageAdapter
from app.infrastructure.repositories.generation_repository import GenerationRepository
from app.infrastructure.repositories.export_repository import ExportRepository
from app.infrastructure.repositories.job_repository import JobRepository
from app.infrastructure.database.connection import get_session
from app.core.dependencies import get_current_user
from app.core.config import get_settings
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/api/v1/exports", tags=["exports"])


# Dependency injection
def get_export_service(session: AsyncSession = Depends(get_session)) -> ExportService:
    """Get export service instance."""
    settings = get_settings()
    renderer = ExportRenderer()
    s3_adapter = S3StorageAdapter(
        bucket_name=settings.s3_bucket_name,
        region=settings.s3_region,
        access_key=settings.aws_access_key_id,
        secret_key=settings.aws_secret_access_key
    )
    generation_repo = GenerationRepository(session)
    export_repo = ExportRepository(session)
    job_repo = JobRepository(session)
    
    return ExportService(
        export_renderer=renderer,
        s3_adapter=s3_adapter,
        generation_repository=generation_repo,
        export_repository=export_repo,
        job_repository=job_repo
    )


@router.post("/pdf", response_model=ExportResponse, status_code=status.HTTP_201_CREATED)
async def export_to_pdf(
    request: ExportRequest,
    current_user: int = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service)
):
    """
    Export a generation to PDF.
    
    - **generation_id**: The generation to export
    - **template**: Template type (modern, classic, creative, ats_optimized)
    - **options**: Optional template customization (fonts, colors, spacing)
    
    Returns presigned download URL valid for 1 hour.
    """
    if request.format != ExportFormat.PDF:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use /api/v1/exports/pdf for PDF exports"
        )
    
    try:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Starting PDF export: user={current_user}, generation={request.generation_id}, template={request.template}")
        
        export = await export_service.export_to_pdf(
            user_id=current_user,
            generation_id=request.generation_id,
            template=request.template,
            options=request.options
        )
        
        logger.info(f"Export successful: export_id={export.id}")
        
        return ExportResponse(
            id=export.id,
            user_id=export.user_id,
            generation_id=export.generation_id,
            format=export.format,
            template=export.template,
            filename=export.filename,
            file_size_bytes=export.file_size_bytes,
            page_count=export.page_count,
            download_url=export.download_url,
            expires_at=export.expires_at,
            created_at=export.created_at,
            metadata=export.export_metadata
        )
    
    except ValueError as e:
        logger.error(f"ValueError in PDF export: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Exception in PDF export: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )


@router.post("/docx", response_model=ExportResponse, status_code=status.HTTP_201_CREATED)
async def export_to_docx(
    request: ExportRequest,
    current_user: int = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service)
):
    """
    Export a generation to DOCX.
    
    - **generation_id**: The generation to export
    - **template**: Template type (modern, classic, creative, ats_optimized)
    - **options**: Optional template customization
    
    Returns presigned download URL valid for 1 hour.
    """
    if request.format != ExportFormat.DOCX:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use /api/v1/exports/docx for DOCX exports"
        )
    
    try:
        export = await export_service.export_to_docx(
            user_id=current_user,
            generation_id=request.generation_id,
            template=request.template,
            options=request.options
        )
        
        return ExportResponse(
            id=export.id,
            user_id=export.user_id,
            generation_id=export.generation_id,
            format=export.format,
            template=export.template,
            filename=export.filename,
            file_size_bytes=export.file_size_bytes,
            page_count=export.page_count,
            download_url=export.download_url,
            expires_at=export.expires_at,
            created_at=export.created_at,
            metadata=export.export_metadata
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )


@router.post("/batch", response_model=BatchExportResponse, status_code=status.HTTP_201_CREATED)
async def batch_export(
    request: BatchExportRequest,
    current_user: int = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service)
):
    """
    Batch export multiple generations to ZIP file.
    
    - **generation_ids**: List of generations to export
    - **template**: Template type to use for all documents
    - **format**: Format for individual files (PDF or DOCX)
    - **options**: Optional template customization
    
    Returns ZIP file with all exported documents.
    """
    try:
        export = await export_service.batch_export(
            user_id=current_user,
            generation_ids=request.generation_ids,
            format=request.format,
            template=request.template,
            options=request.options
        )
        
        return BatchExportResponse(
            id=export.id,
            user_id=export.user_id,
            generation_id=export.generation_id,
            format=export.format,
            template=export.template,
            filename=export.filename,
            file_size_bytes=export.file_size_bytes,
            page_count=export.page_count,
            download_url=export.download_url,
            expires_at=export.expires_at,
            created_at=export.created_at,
            file_count=export.export_metadata.get('file_count'),
            metadata=export.export_metadata
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch export failed: {str(e)}"
        )


@router.get("/templates", response_model=TemplateListResponse)
async def get_templates(
    current_user: int = Depends(get_current_user)
):
    """
    Get list of available export templates.
    
    Returns all available templates with descriptions and default options.
    """
    templates = [
        TemplateInfo(
            id=TemplateType.MODERN,
            name="Modern",
            description="Clean, minimalist design with accent colors and sans-serif fonts. Perfect for tech and creative roles.",
            ats_score=85,
            industries=["Tech", "Startups", "Software"],
            supports_customization={"accent_color": True, "font_family": False},
            preview_url=None,
            default_options={
                "font_family": "Helvetica, Arial, sans-serif",
                "font_size": 11,
                "line_spacing": 1.15,
                "accent_color": "#2563EB"
            }
        ),
        TemplateInfo(
            id=TemplateType.CLASSIC,
            name="Classic",
            description="Traditional, professional design with serif fonts. Ideal for corporate and formal positions.",
            ats_score=95,
            industries=["Corporate", "Finance", "Legal"],
            supports_customization={"accent_color": False, "font_family": True},
            preview_url=None,
            default_options={
                "font_family": "Georgia, Times New Roman, serif",
                "font_size": 11,
                "line_spacing": 1.2
            }
        ),
        TemplateInfo(
            id=TemplateType.CREATIVE,
            name="Creative",
            description="Bold, eye-catching design with sidebar layout and color accents. Great for design and marketing roles.",
            ats_score=75,
            industries=["Design", "Marketing", "Media"],
            supports_customization={"accent_color": True, "font_family": True},
            preview_url=None,
            default_options={
                "font_family": "Helvetica Neue, Arial, sans-serif",
                "font_size": 10.5,
                "line_spacing": 1.3,
                "accent_color": "#2c3e50",
                "secondary_color": "#95a5a6",
                "highlight_color": "#e74c3c"
            }
        ),
        TemplateInfo(
            id=TemplateType.ATS_OPTIMIZED,
            name="ATS-Optimized",
            description="Maximum parsability for Applicant Tracking Systems. Simple text-only layout without complex formatting.",
            ats_score=98,
            industries=["Enterprise", "Government"],
            supports_customization={"accent_color": False, "font_family": False},
            preview_url=None,
            default_options={
                "font_family": "Arial, sans-serif",
                "font_size": 11,
                "line_spacing": 1.15
            }
        )
    ]
    
    return TemplateListResponse(templates=templates)


@router.get("/templates/{template_id}", response_model=TemplateInfo)
async def get_template(
    template_id: TemplateType,
    current_user: int = Depends(get_current_user)
):
    """
    Get details for a specific template.
    
    - **template_id**: Template type (modern, classic, creative, ats_optimized)
    """
    templates_map = {
        TemplateType.MODERN: TemplateInfo(
            id=TemplateType.MODERN,
            name="Modern",
            description="Clean, minimalist design with accent colors and sans-serif fonts.",
            ats_score=85,
            industries=["Tech", "Startups", "Software"],
            supports_customization={"accent_color": True, "font_family": False},
            preview_url=None,
            default_options={
                "font_family": "Helvetica, Arial, sans-serif",
                "font_size": 11,
                "line_spacing": 1.15,
                "accent_color": "#2563EB"
            }
        ),
        TemplateType.CLASSIC: TemplateInfo(
            id=TemplateType.CLASSIC,
            name="Classic",
            description="Traditional, professional design with serif fonts.",
            ats_score=95,
            industries=["Corporate", "Finance", "Legal"],
            supports_customization={"accent_color": False, "font_family": True},
            preview_url=None,
            default_options={
                "font_family": "Georgia, Times New Roman, serif",
                "font_size": 11,
                "line_spacing": 1.2
            }
        ),
        TemplateType.CREATIVE: TemplateInfo(
            id=TemplateType.CREATIVE,
            name="Creative",
            description="Bold, eye-catching design with sidebar layout.",
            ats_score=75,
            industries=["Design", "Marketing", "Media"],
            supports_customization={"accent_color": True, "font_family": True},
            preview_url=None,
            default_options={
                "font_family": "Helvetica Neue, Arial, sans-serif",
                "font_size": 10.5,
                "line_spacing": 1.3,
                "accent_color": "#2c3e50",
                "secondary_color": "#95a5a6",
                "highlight_color": "#e74c3c"
            }
        ),
        TemplateType.ATS_OPTIMIZED: TemplateInfo(
            id=TemplateType.ATS_OPTIMIZED,
            name="ATS-Optimized",
            description="Maximum parsability for ATS systems.",
            ats_score=98,
            industries=["Enterprise", "Government"],
            supports_customization={"accent_color": False, "font_family": False},
            preview_url=None,
            default_options={
                "font_family": "Arial, sans-serif",
                "font_size": 11,
                "line_spacing": 1.15
            }
        )
    }
    
    return templates_map[template_id]


@router.get("/files", response_model=ExportedFileListResponse)
async def list_exports(
    format: Optional[ExportFormat] = None,
    job_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: int = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service)
):
    """
    List user's exported files with pagination.
    
    - **format**: Optional filter by format (pdf, docx, zip)
    - **job_id**: Optional filter by job ID
    - **limit**: Page size (default 50)
    - **offset**: Page offset (default 0)
    
    Returns list of exports with fresh download URLs.
    """
    try:
        exports = await export_service.list_exports(
            user_id=current_user,
            format=format,
            job_id=job_id,
            limit=limit,
            offset=offset
        )
        
        export_responses = [
            ExportResponse(
                id=exp.id,
                user_id=exp.user_id,
                generation_id=exp.generation_id,
                job_id=exp.job_id,
                format=exp.format,
                template=exp.template,
                filename=exp.filename,
                file_size_bytes=exp.file_size_bytes,
                page_count=exp.page_count,
                download_url=exp.download_url,
                local_cache_path=exp.local_cache_path,
                cache_expires_at=exp.cache_expires_at,
                expires_at=exp.expires_at,
                created_at=exp.created_at,
                metadata=exp.export_metadata
            )
            for exp in exports
        ]
        
        return ExportedFileListResponse(
            exports=export_responses,
            total=len(export_responses),
            limit=limit,
            offset=offset
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list exports: {str(e)}"
        )


@router.get("/files/{export_id}/download", response_model=ExportResponse)
async def get_download_url(
    export_id: str,
    current_user: int = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service)
):
    """
    Get fresh download URL for an export.
    
    - **export_id**: Export ID
    
    Returns export with fresh presigned URL (1-hour expiry).
    """
    try:
        export = await export_service.get_export(export_id, current_user)
        
        if not export:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export not found or expired"
            )
        
        return ExportResponse(
            id=export.id,
            user_id=export.user_id,
            generation_id=export.generation_id,
            format=export.format,
            template=export.template,
            filename=export.filename,
            file_size_bytes=export.file_size_bytes,
            page_count=export.page_count,
            download_url=export.download_url,
            expires_at=export.expires_at,
            created_at=export.created_at,
            metadata=export.export_metadata
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get export: {str(e)}"
        )


@router.get("/files/job/{job_id}", response_model=JobExportsResponse)
async def list_job_exports(
    job_id: str,
    format: Optional[ExportFormat] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: int = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service)
):
    """
    List all exports for a specific job, grouped by date.
    
    - **job_id**: Job ID to filter exports
    - **format**: Optional filter by format (pdf, docx, zip)
    - **limit**: Page size (default 100)
    - **offset**: Page offset (default 0)
    
    Returns exports grouped by date (YYYY-MM-DD) with job context.
    Uses optimized composite index (user_id, job_id, created_at).
    """
    try:
        result = await export_service.list_job_exports(
            user_id=current_user,
            job_id=job_id,
            format=format,
            limit=limit,
            offset=offset
        )
        
        # Convert exports to response format
        exports_by_date = {}
        for date_key, exports in result["exports_by_date"].items():
            exports_by_date[date_key] = [
                ExportResponse(
                    id=exp.id,
                    user_id=exp.user_id,
                    generation_id=exp.generation_id,
                    job_id=exp.job_id,
                    format=exp.format,
                    template=exp.template,
                    filename=exp.filename,
                    file_size_bytes=exp.file_size_bytes,
                    page_count=exp.page_count,
                    download_url=exp.download_url,
                    local_cache_path=exp.local_cache_path,
                    cache_expires_at=exp.cache_expires_at,
                    expires_at=exp.expires_at,
                    created_at=exp.created_at,
                    metadata=exp.export_metadata
                )
                for exp in exports
            ]
        
        return JobExportsResponse(
            job_id=result["job_id"],
            job_title=result["job_title"],
            company=result["company"],
            exports_by_date=exports_by_date,
            total_exports=result["total_exports"],
            total_size_bytes=result["total_size_bytes"]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list job exports: {str(e)}"
        )


@router.delete("/files/{export_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_export(
    export_id: str,
    current_user: int = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service)
):
    """
    Delete an export (removes from storage and database).

    - **export_id**: Export ID to delete
    """
    try:
        success = await export_service.delete_export(export_id, current_user)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete export: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_file(
    filename: str,
    token: str,
    expires: int
):
    """
    Download exported file from local storage.
    Used when S3 is not configured (local file fallback).
    
    - **filename**: File name (storage key)
    - **token**: Security token
    - **expires**: Expiration timestamp
    """
    # Validate token and expiration
    current_time = int(datetime.utcnow().timestamp())
    if current_time > expires:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Download link has expired"
        )
    
    # Verify token
    expected_token = hashlib.md5(f"{filename}{expires}".encode()).hexdigest()[:16]
    if token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid download token"
        )
    
    # Get file from local storage
    storage_path = Path(__file__).parent.parent.parent.parent / "storage" / "exports" / filename
    
    if not storage_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Determine content type based on extension
    extension = filename.split('.')[-1].lower()
    content_type_map = {
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'zip': 'application/zip'
    }
    content_type = content_type_map.get(extension, 'application/octet-stream')
    
    return FileResponse(
        path=storage_path,
        media_type=content_type,
        filename=filename
    )
