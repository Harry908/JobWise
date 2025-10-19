"""Generation domain entity."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class GenerationStatus(Enum):
    """Generation pipeline status."""
    PENDING = "pending"
    ANALYZING_JOB = "analyzing_job"
    COMPILING_PROFILE = "compiling_profile"
    GENERATING_DOCUMENTS = "generating_documents"
    VALIDATING_QUALITY = "validating_quality"
    EXPORTING_PDF = "exporting_pdf"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(Enum):
    """Types of generated documents."""
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    LINKEDIN_PROFILE = "linkedin_profile"
    PORTFOLIO_SUMMARY = "portfolio_summary"


@dataclass
class GenerationResult:
    """Result of a document generation."""
    document_type: DocumentType
    content: str
    ats_score: Optional[float]
    word_count: int
    generated_at: datetime
    metadata: Dict[str, Any]


@dataclass
class Generation:
    """Generation entity representing an AI document generation process."""
    id: str
    profile_id: str
    job_id: str
    status: GenerationStatus
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    results: List[GenerationResult]
    error_message: Optional[str]
    processing_time_seconds: Optional[float]
    pipeline_metadata: Dict[str, any]

    @classmethod
    def create(
        cls,
        id: str,
        profile_id: str,
        job_id: str,
    ) -> 'Generation':
        """Create a new generation process."""
        now = datetime.utcnow()
        return cls(
            id=id,
            profile_id=profile_id,
            job_id=job_id,
            status=GenerationStatus.PENDING,
            created_at=now,
            updated_at=now,
            completed_at=None,
            results=[],
            error_message=None,
            processing_time_seconds=None,
            pipeline_metadata={},
        )

    def start_processing(self) -> None:
        """Mark generation as started."""
        self.status = GenerationStatus.ANALYZING_JOB
        self.updated_at = datetime.utcnow()

    def update_status(self, status: GenerationStatus) -> None:
        """Update the generation status."""
        self.status = status
        self.updated_at = datetime.utcnow()

        if status == GenerationStatus.COMPLETED:
            self.completed_at = datetime.utcnow()
            if self.completed_at and self.created_at:
                self.processing_time_seconds = (self.completed_at - self.created_at).total_seconds()

    def add_result(self, result: GenerationResult) -> None:
        """Add a generation result."""
        self.results.append(result)
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error_message: str) -> None:
        """Mark generation as failed."""
        self.status = GenerationStatus.FAILED
        self.error_message = error_message
        self.updated_at = datetime.utcnow()
        self.completed_at = datetime.utcnow()
        if self.completed_at and self.created_at:
            self.processing_time_seconds = (self.completed_at - self.created_at).total_seconds()

    def get_resume_result(self) -> Optional[GenerationResult]:
        """Get the resume generation result."""
        return next(
            (result for result in self.results if result.document_type == DocumentType.RESUME),
            None
        )

    def get_cover_letter_result(self) -> Optional[GenerationResult]:
        """Get the cover letter generation result."""
        return next(
            (result for result in self.results if result.document_type == DocumentType.COVER_LETTER),
            None
        )

    def get_average_ats_score(self) -> Optional[float]:
        """Calculate average ATS score across all results."""
        scores = [r.ats_score for r in self.results if r.ats_score is not None]
        return sum(scores) / len(scores) if scores else None

    def get_total_word_count(self) -> int:
        """Get total word count across all generated documents."""
        return sum(result.word_count for result in self.results)

    def is_completed(self) -> bool:
        """Check if generation is completed."""
        return self.status == GenerationStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if generation failed."""
        return self.status == GenerationStatus.FAILED

    def get_processing_duration(self) -> Optional[float]:
        """Get processing duration in seconds."""
        if not self.completed_at or not self.created_at:
            return None
        return (self.completed_at - self.created_at).total_seconds()

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'job_id': self.job_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'results': [
                {
                    'document_type': result.document_type.value,
                    'content': result.content,
                    'ats_score': result.ats_score,
                    'word_count': result.word_count,
                    'generated_at': result.generated_at.isoformat(),
                    'metadata': result.metadata,
                }
                for result in self.results
            ],
            'error_message': self.error_message,
            'processing_time_seconds': self.processing_time_seconds,
            'pipeline_metadata': self.pipeline_metadata,
        }