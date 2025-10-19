"""Common pipeline interfaces and types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from ..entities.profile import MasterProfile
from ..entities.job import JobPosting
from ..entities.generation import Generation


class PipelineStage(Enum):
    """Pipeline execution stages."""
    ANALYZING_JOB = "analyzing_job"
    COMPILING_PROFILE = "compiling_profile"
    GENERATING_DOCUMENTS = "generating_documents"
    VALIDATING_QUALITY = "validating_quality"
    EXPORTING_PDF = "exporting_pdf"


@dataclass
class PipelineContext:
    """Context passed through pipeline stages."""
    profile: MasterProfile
    job: JobPosting
    generation: Generation
    metadata: Dict[str, Any]

    def update_metadata(self, key: str, value: Any) -> None:
        """Update pipeline metadata."""
        self.metadata[key] = value
        self.metadata['updated_at'] = datetime.utcnow().isoformat()


class PipelineError(Exception):
    """Base exception for pipeline errors."""
    pass


class StageError(PipelineError):
    """Error in a specific pipeline stage."""
    def __init__(self, stage: PipelineStage, message: str, cause: Optional[Exception] = None):
        self.stage = stage
        self.message = message
        self.cause = cause
        super().__init__(f"Stage {stage.value}: {message}")


class PipelineStageInterface(ABC):
    """Interface for pipeline stages."""

    @abstractmethod
    async def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute the stage with the given context."""
        pass

    @property
    @abstractmethod
    def stage(self) -> PipelineStage:
        """Return the pipeline stage this implements."""
        pass