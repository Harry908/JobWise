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
    format: ExportFormat
    template: TemplateType
    filename: str
    file_path: str  # S3 object key
    file_size_bytes: int
    page_count: Optional[int] = None  # PDF only
    options: Optional[str] = None  # JSON string
    export_metadata: Optional[str] = None  # JSON string
    download_url: Optional[str] = None
    expires_at: datetime = None
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
    
    def generate_s3_key(self) -> str:
        """Generate S3 object key for this export."""
        extension = self.format.value
        return f"exports/{self.user_id}/{self.id}.{extension}"
