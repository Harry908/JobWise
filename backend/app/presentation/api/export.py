"""
Export API Router
Endpoints for document export (PDF/DOCX/ZIP).
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.domain.enums.export_format import ExportFormat
from app.domain.enums.template_type import TemplateType
from app.presentation.schemas.export import (
    ExportRequest,
    ExportResponse,
    BatchExportRequest,
    BatchExportResponse,
    TemplateInfo,
    TemplateListResponse,
    ExportedFileListResponse
)
from app.application.services.export_service import ExportService
from app.application.services.export_renderer import ExportRenderer
from app.infrastructure.storage.s3_storage_adapter import S3StorageAdapter
from app.infrastructure.repositories.generation_repository import GenerationRepository
from app.infrastructure.repositories.export_repository import ExportRepository
from app.infrastructure.database.connection import get_session
from app.core.dependencies import get_current_user
from app.domain.entities.user import User
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/api/v1/exports", tags=["exports"])


# Dependency injection
def get_export_service(session: AsyncSession = Depends(get_session)) -> ExportService:
    """Get export service instance."""
    renderer = ExportRenderer()
    s3_adapter = S3StorageAdapter()
    generation_repo = GenerationRepository(session)
    export_repo = ExportRepository(session)
    
    return ExportService(
        export_renderer=renderer,
        s3_adapter=s3_adapter,
        generation_repository=generation_repo,
        export_repository=export_repo
    )


@router.post("/pdf", response_model=ExportResponse, status_code=status.HTTP_201_CREATED)
async def export_to_pdf(
    request: ExportRequest,
    current_user: User = Depends(get_current_user),
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
        export = await export_service.export_to_pdf(
            user_id=current_user.id,
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


@router.post("/docx", response_model=ExportResponse, status_code=status.HTTP_201_CREATED)
async def export_to_docx(
    request: ExportRequest,
    current_user: User = Depends(get_current_user),
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
            user_id=current_user.id,
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
    current_user: User = Depends(get_current_user),
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
            user_id=current_user.id,
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
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
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
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service)
):
    """
    List user's exported files with pagination.
    
    - **format**: Optional filter by format (pdf, docx, zip)
    - **limit**: Page size (default 50)
    - **offset**: Page offset (default 0)
    
    Returns list of exports with fresh download URLs.
    """
    try:
        exports = await export_service.list_exports(
            user_id=current_user.id,
            format=format,
            limit=limit,
            offset=offset
        )
        
        export_responses = [
            ExportResponse(
                id=exp.id,
                user_id=exp.user_id,
                generation_id=exp.generation_id,
                format=exp.format,
                template=exp.template,
                filename=exp.filename,
                file_size_bytes=exp.file_size_bytes,
                page_count=exp.page_count,
                download_url=exp.download_url,
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
    current_user: User = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service)
):
    """
    Get fresh download URL for an export.
    
    - **export_id**: Export ID
    
    Returns export with fresh presigned URL (1-hour expiry).
    """
    try:
        export = await export_service.get_export(export_id, current_user.id)
        
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


@router.delete("/files/{export_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_export(
    export_id: str,
    current_user: User = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service)
):
    """
    Delete an export (removes from S3 and database).
    
    - **export_id**: Export ID to delete
    """
    try:
        success = await export_service.delete_export(export_id, current_user.id)
        
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
