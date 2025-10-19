"""AI Orchestrator core for the 5-stage generation pipeline."""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from openai import AsyncOpenAI, OpenAIError

from ...core.config import get_settings
from ..entities.profile import MasterProfile
from ..entities.job import JobPosting
from ..entities.generation import Generation, GenerationResult, DocumentType, GenerationStatus
from ..value_objects import PersonalInfo, Experience, Education, Skills, Project
from .stages.job_analyzer import JobAnalyzerStage
from .stages.profile_compiler import ProfileCompilerStage
from .stages.document_generator import DocumentGeneratorStage
from .stages.quality_validator import QualityValidatorStage
from .stages.pdf_exporter import PDFExporterStage
from .pipeline_common import PipelineStage, PipelineContext, PipelineError, StageError, PipelineStageInterface


class AIOrchestrator:
    """Core AI orchestrator managing the 5-stage generation pipeline."""

    def __init__(self, openai_client: Optional[AsyncOpenAI] = None):
        """Initialize the orchestrator."""
        self.settings = get_settings()
        self.openai_client = openai_client or AsyncOpenAI(
            api_key=self.settings.openai_api_key,
            timeout=self.settings.openai_timeout,
            max_retries=self.settings.openai_max_retries,
        )
        self.stages: List[PipelineStageInterface] = []
        self._stage_status_map = {
            PipelineStage.ANALYZING_JOB: GenerationStatus.ANALYZING_JOB,
            PipelineStage.COMPILING_PROFILE: GenerationStatus.COMPILING_PROFILE,
            PipelineStage.GENERATING_DOCUMENTS: GenerationStatus.GENERATING_DOCUMENTS,
            PipelineStage.VALIDATING_QUALITY: GenerationStatus.VALIDATING_QUALITY,
            PipelineStage.EXPORTING_PDF: GenerationStatus.EXPORTING_PDF,
        }
        self._setup_stages()

    def _setup_stages(self) -> None:
        """Setup the 5-stage pipeline."""
        self.stages = [
            JobAnalyzerStage(self.openai_client),
            ProfileCompilerStage(self.openai_client),
            DocumentGeneratorStage(self.openai_client),
            QualityValidatorStage(self.openai_client),
            PDFExporterStage(self.openai_client),
        ]

    async def execute_pipeline(
        self,
        profile: MasterProfile,
        job: JobPosting,
        generation_id: str,
    ) -> Generation:
        """Execute the complete 5-stage pipeline."""
        # Create generation entity
        generation = Generation.create(generation_id, str(profile.id), str(job.id))

        # Create pipeline context
        context = PipelineContext(
            profile=profile,
            job=job,
            generation=generation,
            metadata={
                'started_at': datetime.utcnow().isoformat(),
                'pipeline_version': '1.0',
            }
        )

        try:
            # Execute each stage
            for stage in self.stages:
                logger.info(f"Starting pipeline stage: {stage.stage.value}")
                context.generation.update_status(self._stage_status_map[stage.stage])

                # Execute stage with retry logic
                context = await self._execute_stage_with_retry(stage, context)

                logger.info(f"Completed pipeline stage: {stage.stage.value}")

            # Mark as completed
            context.generation.update_status(GenerationStatus.COMPLETED)
            context.update_metadata('completed_at', datetime.utcnow().isoformat())

            logger.info(f"Pipeline completed successfully for generation {generation_id}")
            return context.generation

        except Exception as e:
            logger.error(f"Pipeline failed for generation {generation_id}: {str(e)}")
            context.generation.mark_failed(str(e))
            context.update_metadata('failed_at', datetime.utcnow().isoformat())
            context.update_metadata('error', str(e))
            raise PipelineError(f"Pipeline execution failed: {str(e)}") from e

    async def _execute_stage_with_retry(
        self,
        stage: PipelineStageInterface,
        context: PipelineContext,
        max_retries: int = 3,
    ) -> PipelineContext:
        """Execute a stage with retry logic."""
        last_error = None

        for attempt in range(max_retries):
            try:
                return await stage.execute(context)
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Stage {stage.stage.value} failed on attempt {attempt + 1}/{max_retries}: {str(e)}"
                )

                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = (2 ** attempt) * 1.0  # Base delay of 1 second
                    await asyncio.sleep(wait_time)

        # All retries failed
        raise StageError(
            stage.stage,
            f"Failed after {max_retries} attempts: {str(last_error)}",
            last_error
        )

    async def get_pipeline_status(self, generation_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a pipeline execution."""
        # This would typically query a database or cache
        # For now, return None as we don't have persistence yet
        return None

    def get_available_stages(self) -> List[str]:
        """Get list of available pipeline stages."""
        return [stage.stage.value for stage in self.stages]