"""
Export API Schemas
Request/response models for export endpoints.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.domain.enums.export_format import ExportFormat
from app.domain.enums.template_type import TemplateType


class ExportRequest(BaseModel):
    """Request to export a generation."""
    generation_id: str = Field(..., description="Generation ID to export")
    template: TemplateType = Field(..., description="Template type to use")
    format: ExportFormat = Field(..., description="Export format (PDF or DOCX)")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Template customization options")


class BatchExportRequest(BaseModel):
    """Request to batch export multiple generations."""
    generation_ids: List[str] = Field(..., description="List of generation IDs to export")
    template: TemplateType = Field(..., description="Template type to use")
    format: ExportFormat = Field(..., description="Format for individual files (PDF or DOCX)")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Template customization options")


class ExportResponse(BaseModel):
    """Export response."""
    id: str = Field(..., description="Export ID")
    user_id: int = Field(..., description="User ID")
    generation_id: Optional[str] = Field(None, description="Generation ID (null for batch exports)")
    format: ExportFormat = Field(..., description="Export format")
    template: TemplateType = Field(..., description="Template used")
    filename: str = Field(..., description="Filename")
    file_size_bytes: int = Field(..., description="File size in bytes")
    page_count: Optional[int] = Field(None, description="Page count (PDF only)")
    download_url: str = Field(..., description="Presigned download URL (1-hour expiry)")
    expires_at: datetime = Field(..., description="Export expiry date (30 days)")
    created_at: datetime = Field(..., description="Creation timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": 1,
                "generation_id": "660e8400-e29b-41d4-a716-446655440000",
                "format": "pdf",
                "template": "modern",
                "filename": "resume_20240115_143022.pdf",
                "file_size_bytes": 245678,
                "page_count": 2,
                "download_url": "https://jobsync-exports.s3.amazonaws.com/...",
                "expires_at": "2024-02-14T14:30:22Z",
                "created_at": "2024-01-15T14:30:22Z",
                "metadata": {
                    "generation_type": "resume",
                    "created_from": "660e8400-e29b-41d4-a716-446655440000"
                }
            }
        }


class BatchExportResponse(ExportResponse):
    """Batch export response (ZIP file)."""
    file_count: Optional[int] = Field(None, description="Number of files in ZIP")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "user_id": 1,
                "generation_id": None,
                "format": "zip",
                "template": "modern",
                "filename": "batch_export_20240115_143500.zip",
                "file_size_bytes": 512345,
                "page_count": None,
                "download_url": "https://jobsync-exports.s3.amazonaws.com/...",
                "expires_at": "2024-02-14T14:35:00Z",
                "created_at": "2024-01-15T14:35:00Z",
                "file_count": 3,
                "metadata": {
                    "generation_ids": ["abc", "def", "ghi"],
                    "individual_format": "pdf"
                }
            }
        }


class TemplateInfo(BaseModel):
    """Template information."""
    id: TemplateType = Field(..., description="Template ID")
    name: str = Field(..., description="Template display name")
    description: str = Field(..., description="Template description")
    preview_url: Optional[str] = Field(None, description="Preview image URL")
    default_options: Dict[str, Any] = Field(..., description="Default styling options")


class TemplateListResponse(BaseModel):
    """List of available templates."""
    templates: List[TemplateInfo] = Field(..., description="Available templates")


class ExportedFileListResponse(BaseModel):
    """List of exported files."""
    exports: List[ExportResponse] = Field(..., description="List of exports")
    total: int = Field(..., description="Total count")
    limit: int = Field(..., description="Page size")
    offset: int = Field(..., description="Page offset")
    
    class Config:
        json_schema_extra = {
            "example": {
                "exports": [],
                "total": 15,
                "limit": 10,
                "offset": 0
            }
        }
