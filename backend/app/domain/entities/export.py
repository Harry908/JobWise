"""Export entity."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from ..enums.export_format import ExportFormat
from ..enums.template_type import TemplateType


@dataclass
class Export:
    """Exported document."""
    
    id: UUID
    user_id: int
    generation_id: UUID
    job_id: UUID  # Denormalized from generations.job_id for efficient queries
    format: ExportFormat
    template: TemplateType
    filename: str
    file_path: str  # S3 object key
    file_size_bytes: int
    page_count: Optional[int] = None  # PDF only
    options: Optional[str] = None  # JSON string
    export_metadata: Optional[str] = None  # JSON string (includes job title, company, ats_score)
    download_url: Optional[str] = None
    local_cache_path: Optional[str] = None  # Mobile local cache path (platform-specific)
    cache_expires_at: Optional[datetime] = None  # Cache expiration (typically 7 days)
    expires_at: datetime = None  # S3 expiration (30 days)
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.expires_at is None:
            # Default 30 days retention
            self.expires_at = self.created_at + timedelta(days=30)
    
    def is_expired(self) -> bool:
        """Check if export has expired."""
        return datetime.utcnow() > self.expires_at
    
    @staticmethod
    def generate_s3_key(user_id: int, export_id: str, format: 'ExportFormat') -> str:
        """Generate S3 object key for export.
        
        Args:
            user_id: User ID
            export_id: Export ID
            format: Export format
            
        Returns:
            S3 object key path
        """
        extension = format.value
        return f"exports/{user_id}/{export_id}.{extension}"
