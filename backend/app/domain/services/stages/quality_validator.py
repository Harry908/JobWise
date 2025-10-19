"""Quality Validator Stage - Stage 4 of the AI generation pipeline."""

import re
import logging
from typing import Dict, Any, List

from ..ai_orchestrator import PipelineStageInterface, PipelineStage, PipelineContext, StageError
from ...entities.generation import DocumentType


logger = logging.getLogger(__name__)


class QualityValidatorStage(PipelineStageInterface):
    """Stage 4: Validate document quality and ATS compatibility."""

    def __init__(self, openai_client=None):  # Not needed for validation
        self.openai_client = openai_client

    @property
    def stage(self) -> PipelineStage:
        return PipelineStage.VALIDATING_QUALITY

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """Validate the quality of generated documents."""
        try:
            # Validate all generated documents
            validation_results = {}
            overall_score = 0.0

            for result in context.generation.results:
                doc_validation = self._validate_document(result, context.job, context.metadata)
                validation_results[result.document_type.value] = doc_validation

                if result.document_type == DocumentType.RESUME:
                    overall_score = doc_validation.get('ats_score', 0.0)
                elif result.document_type == DocumentType.COVER_LETTER:
                    # Weight cover letter score less heavily
                    overall_score = (overall_score + doc_validation.get('quality_score', 0.0)) / 2

            # Update generation with validation scores
            for result in context.generation.results:
                if result.document_type == DocumentType.RESUME:
                    result.ats_score = validation_results.get('resume', {}).get('ats_score')

            # Update context metadata
            context.update_metadata('quality_validation', validation_results)
            context.update_metadata('overall_quality_score', overall_score)
            context.update_metadata('stage_4_completed', True)

            logger.info(f"Quality validation completed with score: {overall_score}")
            return context

        except Exception as e:
            logger.error(f"Quality validation failed: {str(e)}")
            raise StageError(self.stage, f"Failed to validate document quality: {str(e)}", e)

    def _validate_document(self, document_result, job, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single document for quality and ATS compatibility."""
        content = document_result.content
        doc_type = document_result.document_type

        validation = {
            'word_count': len(content.split()),
            'character_count': len(content),
            'has_contact_info': False,
            'has_summary': False,
            'formatting_issues': [],
            'quality_score': 0.0
        }

        if doc_type == DocumentType.RESUME:
            validation.update(self._validate_resume(content, job, metadata))
        elif doc_type == DocumentType.COVER_LETTER:
            validation.update(self._validate_cover_letter(content, job, metadata))

        # Calculate overall quality score
        validation['quality_score'] = self._calculate_quality_score(validation)

        return validation

    def _validate_resume(self, content: str, job, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate resume-specific criteria."""
        validation = {
            'ats_score': 0.0,
            'keyword_matches': 0,
            'has_experience_section': False,
            'has_education_section': False,
            'has_skills_section': False,
            'experience_years_mentioned': False,
            'quantified_achievements': 0,
        }

        content_lower = content.lower()

        # Check for ATS keywords
        job_analysis = metadata.get('job_analysis', {})
        ats_keywords = set(job_analysis.get('ats_keywords', []))
        content_words = set(re.findall(r'\b\w+\b', content_lower))

        matched_keywords = ats_keywords.intersection(content_words)
        validation['keyword_matches'] = len(matched_keywords)
        validation['ats_score'] = len(matched_keywords) / len(ats_keywords) if ats_keywords else 0.5

        # Check for required sections
        validation['has_experience_section'] = 'experience' in content_lower
        validation['has_education_section'] = 'education' in content_lower
        validation['has_skills_section'] = 'skills' in content_lower or 'technologies' in content_lower

        # Check for contact information
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        validation['has_contact_info'] = bool(re.search(email_pattern, content) or re.search(phone_pattern, content))

        # Check for quantified achievements (numbers indicating metrics)
        number_pattern = r'\b\d+(\.\d+)?%?\b'
        validation['quantified_achievements'] = len(re.findall(number_pattern, content))

        # Check for professional summary
        validation['has_summary'] = 'summary' in content_lower or len(content.split('\n\n')[0].split()) > 20

        return validation

    def _validate_cover_letter(self, content: str, job, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate cover letter-specific criteria."""
        validation = {
            'has_greeting': False,
            'has_company_reference': False,
            'has_position_reference': False,
            'has_call_to_action': False,
            'personalization_score': 0.0,
            'structure_score': 0.0,
        }

        content_lower = content.lower()

        # Check for proper greeting
        greeting_patterns = [r'dear\s+\w+', r'hello\s+\w+', r'hi\s+\w+']
        validation['has_greeting'] = any(re.search(pattern, content_lower) for pattern in greeting_patterns)

        # Check for company and position references
        validation['has_company_reference'] = job.company.lower() in content_lower
        validation['has_position_reference'] = job.title.lower() in content_lower

        # Check for call to action
        cta_phrases = ['look forward to', 'would welcome', 'excited to discuss', 'contact me', 'available to']
        validation['has_call_to_action'] = any(phrase in content_lower for phrase in cta_phrases)

        # Basic structure check (paragraphs)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        validation['structure_score'] = min(1.0, len(paragraphs) / 4.0)  # Expect 3-4 paragraphs

        # Personalization score based on references to specific job details
        personalization_indicators = 0
        job_keywords = set(metadata.get('job_analysis', {}).get('industry_keywords', []))
        content_words = set(re.findall(r'\b\w+\b', content_lower))
        personalization_indicators += len(job_keywords.intersection(content_words))

        if validation['has_company_reference']:
            personalization_indicators += 1
        if validation['has_position_reference']:
            personalization_indicators += 1

        validation['personalization_score'] = min(1.0, personalization_indicators / 5.0)

        return validation

    def _calculate_quality_score(self, validation: Dict[str, Any]) -> float:
        """Calculate overall quality score from validation metrics."""
        score = 0.0
        total_weight = 0.0

        # ATS score (for resumes)
        if 'ats_score' in validation:
            score += validation['ats_score'] * 0.4
            total_weight += 0.4

        # Structure and completeness
        structure_indicators = [
            validation.get('has_contact_info', False),
            validation.get('has_summary', False),
            validation.get('has_experience_section', False),
            validation.get('has_education_section', False),
            validation.get('has_skills_section', False),
            validation.get('has_greeting', False),
            validation.get('has_company_reference', False),
            validation.get('has_position_reference', False),
            validation.get('has_call_to_action', False),
        ]

        structure_score = sum(structure_indicators) / len(structure_indicators)
        score += structure_score * 0.3
        total_weight += 0.3

        # Content quality indicators
        content_score = 0.0
        if validation.get('word_count', 0) > 300:  # Minimum viable length
            content_score += 0.3
        if validation.get('quantified_achievements', 0) > 2:  # Has metrics
            content_score += 0.3
        if validation.get('keyword_matches', 0) > 5:  # Good keyword coverage
            content_score += 0.4

        score += content_score * 0.3
        total_weight += 0.3

        return score / total_weight if total_weight > 0 else 0.0