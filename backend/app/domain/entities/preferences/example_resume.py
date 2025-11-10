"""Example resume domain entity."""

from datetime import datetime
from typing import Optional, Dict, Literal
from pydantic import BaseModel, Field
import uuid
import hashlib


class FileMetadata(BaseModel):
    """File metadata for uploaded documents."""
    file_name: str
    file_size: int  # bytes
    file_type: str  # MIME type
    file_extension: str
    upload_source: Literal["web", "mobile", "api"] = "web"
    content_hash: str  # SHA-256 of file content
    virus_scan_status: Literal["pending", "clean", "infected", "error"] = "pending"


class ExampleResume(BaseModel):
    """Example resume uploaded by user for preference extraction."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int
    
    # File information
    file_metadata: FileMetadata
    storage_path: str  # Path to stored file
    storage_provider: Literal["local", "s3", "azure"] = "local"
    
    # Content extraction
    extracted_text: Optional[str] = None  # Extracted plain text
    text_extraction_status: Literal["pending", "completed", "failed"] = "pending"
    text_extraction_error: Optional[str] = None
    
    # Analysis status
    structural_analysis_completed: bool = Field(default=False)
    layout_config_id: Optional[str] = None  # Generated layout config
    analysis_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Usage tracking
    is_primary_example: bool = Field(default=False)  # User's main reference resume
    usage_count: int = Field(default=0)  # How many times used for generation
    
    # Quality assessment
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)  # Overall resume quality
    ats_compatibility_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    professional_polish_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # User feedback
    user_rating: Optional[int] = Field(None, ge=1, le=5)  # User's rating of this example
    user_notes: Optional[str] = Field(None, max_length=500)
    
    # Status and lifecycle
    status: Literal["uploaded", "processing", "analyzed", "active", "archived", "failed"] = "uploaded"
    archived_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_analyzed_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @classmethod
    def create_from_upload(
        cls,
        user_id: int,
        file_name: str,
        file_content: bytes,
        file_type: str,
        storage_path: str,
        upload_source: Literal["web", "mobile", "api"] = "web"
    ) -> "ExampleResume":
        """Create ExampleResume from file upload."""
        # Calculate content hash
        content_hash = hashlib.sha256(file_content).hexdigest()
        
        # Extract file extension
        file_extension = file_name.split('.')[-1].lower() if '.' in file_name else ''
        
        file_metadata = FileMetadata(
            file_name=file_name,
            file_size=len(file_content),
            file_type=file_type,
            file_extension=file_extension,
            upload_source=upload_source,
            content_hash=content_hash
        )
        
        return cls(
            user_id=user_id,
            file_metadata=file_metadata,
            storage_path=storage_path,
            status="uploaded"
        )
    
    def mark_as_primary(self):
        """Mark this resume as the user's primary example."""
        self.is_primary_example = True
        self.updated_at = datetime.utcnow()
    
    def update_analysis_results(
        self,
        layout_config_id: str,
        analysis_confidence: float,
        quality_scores: Optional[Dict[str, float]] = None
    ):
        """Update with structural analysis results."""
        self.layout_config_id = layout_config_id
        self.analysis_confidence = analysis_confidence
        self.structural_analysis_completed = True
        self.status = "analyzed"
        self.last_analyzed_at = datetime.utcnow()
        
        if quality_scores:
            self.quality_score = quality_scores.get("overall")
            self.ats_compatibility_score = quality_scores.get("ats_compatibility")
            self.professional_polish_score = quality_scores.get("professional_polish")
        
        self.updated_at = datetime.utcnow()
    
    def update_text_extraction(
        self, 
        extracted_text: str, 
        status: Literal["pending", "completed", "failed"] = "completed", 
        error: Optional[str] = None
    ):
        """Update text extraction results."""
        self.extracted_text = extracted_text
        self.text_extraction_status = status
        self.text_extraction_error = error
        self.updated_at = datetime.utcnow()
    
    def record_usage(self):
        """Record that this example was used for generation."""
        self.usage_count += 1
        self.updated_at = datetime.utcnow()
    
    def archive(self, reason: str = "User archived"):
        """Archive this example resume."""
        self.status = "archived"
        self.archived_at = datetime.utcnow()
        self.user_notes = f"{self.user_notes or ''}\nArchived: {reason}".strip()
        self.updated_at = datetime.utcnow()
    
    def is_ready_for_analysis(self) -> bool:
        """Check if resume is ready for structural analysis."""
        return (
            self.status in ["uploaded", "processing"] and
            self.text_extraction_status == "completed" and
            self.extracted_text is not None and
            len(self.extracted_text.strip()) > 100  # Minimum content check
        )
    
    def is_usable_for_generation(self) -> bool:
        """Check if resume can be used for generation preference extraction."""
        return (
            self.status == "analyzed" and
            self.structural_analysis_completed and
            self.layout_config_id is not None and
            self.analysis_confidence >= 0.5  # Minimum confidence threshold
        )