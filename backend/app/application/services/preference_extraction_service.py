"""Service for extracting user preferences from uploaded documents."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import json

from app.domain.entities.preferences.writing_style_config import WritingStyleConfig
from app.domain.entities.preferences.layout_config import LayoutConfig  
from app.domain.entities.preferences.user_generation_profile import UserGenerationProfile
from app.domain.entities.preferences.example_resume import ExampleResume
from app.domain.prompts.writing_style_prompts import WritingStylePrompts
from app.domain.prompts.structural_analysis_prompts import StructuralAnalysisPrompts
from app.infrastructure.adapters.groq_adapter import GroqAdapter
from app.core.exceptions import PreferenceExtractionException
from app.application.services.file_upload.text_extraction_service import TextExtractionService
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class PreferenceExtractionService:
    """Service for extracting user preferences from cover letters and example resumes."""
    
    def __init__(self, groq_adapter: GroqAdapter, text_extraction_service: TextExtractionService):
        """
        Initialize preference extraction service.
        
        Args:
            groq_adapter: Groq LLM adapter for analysis
            text_extraction_service: Service for extracting text from files
        """
        self.groq = groq_adapter
        self.text_extractor = text_extraction_service
        self.writing_style_prompts = WritingStylePrompts()
        self.structural_prompts = StructuralAnalysisPrompts()

    async def extract_writing_style_from_cover_letter(
        self,
        file_path: str,
        user_id: int,
        context: Optional[Dict[str, Any]] = None
    ) -> WritingStyleConfig:
        """
        Extract writing style preferences from a cover letter.
        
        Args:
            file_path: Path to the cover letter file
            user_id: User ID
            context: Additional context for analysis
            
        Returns:
            WritingStyleConfig with extracted preferences
            
        Raises:
            PreferenceExtractionException: Extraction failed
        """
        try:
            logger.info(f"Extracting writing style from cover letter: {file_path}")
            
            # Extract text from file
            extraction_result = await self.text_extractor.extract_text(file_path)
            
            if not extraction_result.get("success"):
                raise PreferenceExtractionException(f"Failed to extract text: {extraction_result.get('error')}")
            
            text_content = extraction_result["text"]
            
            if len(text_content.strip()) < 100:
                raise PreferenceExtractionException("Cover letter text too short for meaningful analysis")
            
            # Build analysis context
            analysis_context = {
                "user_id": user_id,
                "file_type": "cover_letter",
                "file_name": Path(file_path).name,
                "word_count": extraction_result.get("statistics", {}).get("word_count", 0),
                **(context or {})
            }
            
            # Create analysis prompt
            analysis_prompt = self.writing_style_prompts.create_style_analysis_prompt(
                cover_letter_text=text_content,
                context=analysis_context
            )
            
            # Get LLM analysis
            logger.debug("Sending cover letter to LLM for writing style analysis")
            analysis_response = await self.groq.generate(
                prompt=analysis_prompt,
                temperature=settings.llm_temperature_preference,  # Low temperature for consistent analysis
                max_tokens=settings.llm_max_tokens_preference
            )
            
            # Parse LLM response into structured preferences
            style_config = self._parse_writing_style_response(analysis_response, user_id)
            
            # Store the full verbatim cover letter text
            style_config.source_text = text_content
            
            # Add metadata
            style_config.source_document = Path(file_path).name
            style_config.extraction_metadata = {
                "extracted_at": datetime.now().isoformat(),
                "word_count": extraction_result.get("statistics", {}).get("word_count", 0),
                "confidence_score": self._calculate_confidence_score(text_content),
                "analysis_context": analysis_context
            }
            
            logger.info(f"Successfully extracted writing style preferences for user {user_id}")
            return style_config
            
        except Exception as e:
            logger.error(f"Writing style extraction failed: {e}")
            raise PreferenceExtractionException(f"Failed to extract writing style: {str(e)}")

    async def extract_layout_from_example_resume(
        self,
        file_path: str,
        user_id: int,
        context: Optional[Dict[str, Any]] = None
    ) -> LayoutConfig:
        """
        Extract layout preferences from an example resume.
        
        Args:
            file_path: Path to the example resume file
            user_id: User ID
            context: Additional context for analysis
            
        Returns:
            LayoutConfig with extracted preferences
            
        Raises:
            PreferenceExtractionException: Extraction failed
        """
        try:
            logger.info(f"Extracting layout preferences from resume: {file_path}")
            
            # Extract text from file
            extraction_result = await self.text_extractor.extract_text(file_path)
            
            if not extraction_result.get("success"):
                raise PreferenceExtractionException(f"Failed to extract text: {extraction_result.get('error')}")
            
            text_content = extraction_result["text"]
            
            if len(text_content.strip()) < 200:
                raise PreferenceExtractionException("Resume text too short for meaningful analysis")
            
            # Build analysis context
            analysis_context = {
                "user_id": user_id,
                "file_type": "example_resume",
                "file_name": Path(file_path).name,
                "word_count": extraction_result.get("statistics", {}).get("word_count", 0),
                "detected_sections": extraction_result.get("statistics", {}).get("sections", []),
                **(context or {})
            }
            
            # Create structural analysis prompt
            analysis_prompt = self.structural_prompts.create_layout_analysis_prompt(
                resume_text=text_content,
                context=analysis_context
            )
            
            # Get LLM analysis
            logger.debug("Sending resume to LLM for layout analysis")
            analysis_response = await self.groq.generate(
                prompt=analysis_prompt,
                temperature=settings.llm_temperature_preference,  # Low temperature for consistent analysis
                max_tokens=settings.llm_max_tokens_preference
            )
            
            # Parse LLM response into structured layout preferences
            layout_config = self._parse_layout_response(analysis_response, user_id)
            
            # Add metadata
            layout_config.source_document = Path(file_path).name
            layout_config.extraction_metadata = {
                "extracted_at": datetime.now().isoformat(),
                "word_count": extraction_result.get("statistics", {}).get("word_count", 0),
                "detected_sections": extraction_result.get("statistics", {}).get("sections", []),
                "confidence_score": self._calculate_confidence_score(text_content),
                "analysis_context": analysis_context
            }
            
            logger.info(f"Successfully extracted layout preferences for user {user_id}")
            return layout_config
            
        except Exception as e:
            logger.error(f"Layout extraction failed: {e}")
            raise PreferenceExtractionException(f"Failed to extract layout preferences: {str(e)}")

    async def create_user_generation_profile(
        self,
        user_id: int,
        writing_style_config: WritingStyleConfig,
        layout_config: LayoutConfig,
        example_resumes: Optional[List[ExampleResume]] = None
    ) -> UserGenerationProfile:
        """
        Create a comprehensive user generation profile.
        
        Args:
            user_id: User ID
            writing_style_config: Extracted writing style preferences
            layout_config: Extracted layout preferences
            example_resumes: Optional list of example resumes
            
        Returns:
            Complete UserGenerationProfile
        """
        try:
            logger.info(f"Creating user generation profile for user {user_id}")
            
            # Calculate overall quality score
            style_confidence = writing_style_config.extraction_metadata.get("confidence_score", 0.5)
            layout_confidence = layout_config.extraction_metadata.get("confidence_score", 0.5)
            overall_quality = (style_confidence + layout_confidence) / 2
            
            # Determine generation preferences based on extracted configs
            generation_preferences = {
                "prioritize_style_consistency": True,
                "prioritize_layout_consistency": True,
                "adapt_tone_to_industry": True,
                "maintain_personal_voice": True,
                "prefer_detailed_descriptions": writing_style_config.sentence_structure == "detailed",
                "prefer_quantified_achievements": "quantified" in (writing_style_config.achievement_style or ""),
                "use_action_verbs": writing_style_config.action_verb_style == "strong",
                "maintain_section_order": layout_config.section_order_preference == "consistent"
            }
            
            profile = UserGenerationProfile(
                user_id=user_id,
                writing_style_config_id=writing_style_config.id,
                layout_config_id=layout_config.id,
                overall_quality_score=overall_quality,
                is_active=True,
                generation_preferences=generation_preferences,
                last_updated=datetime.now(),
                example_resumes=example_resumes or []
            )
            
            logger.info(f"Created generation profile with quality score: {overall_quality:.2f}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create user generation profile: {e}")
            raise PreferenceExtractionException(f"Failed to create generation profile: {str(e)}")

    def _parse_writing_style_response(self, llm_response: str, user_id: int) -> WritingStyleConfig:
        """
        Parse LLM response into WritingStyleConfig.
        
        Args:
            llm_response: Raw LLM response
            user_id: User ID
            
        Returns:
            Parsed WritingStyleConfig
        """
        try:
            # Try to extract JSON from LLM response
            response_data = self._extract_json_from_response(llm_response)
            
            # Map LLM analysis to WritingStyleConfig fields
            config = WritingStyleConfig(
                user_id=user_id,
                tone_preference=response_data.get("tone", "professional"),
                formality_level=response_data.get("formality", "formal"),
                sentence_structure=response_data.get("sentence_structure", "varied"),
                vocabulary_complexity=response_data.get("vocabulary", "intermediate"),
                personal_pronouns_usage=response_data.get("pronouns", "minimal"),
                achievement_style=response_data.get("achievements", "action-focused"),
                action_verb_style=response_data.get("action_verbs", "strong"),
                industry_language_adaptation=response_data.get("industry_language", True),
                confidence_level=response_data.get("confidence", "moderate"),
                authenticity_markers=response_data.get("authenticity_markers", []),
                communication_patterns=response_data.get("communication_patterns", {}),
                is_active=True
            )
            
            return config
            
        except Exception as e:
            logger.warning(f"Failed to parse LLM response, using default config: {e}")
            # Return default config if parsing fails
            return WritingStyleConfig(
                user_id=user_id,
                tone_preference="professional",
                formality_level="formal",
                is_active=True
            )

    def _parse_layout_response(self, llm_response: str, user_id: int) -> LayoutConfig:
        """
        Parse LLM response into LayoutConfig.
        
        Args:
            llm_response: Raw LLM response
            user_id: User ID
            
        Returns:
            Parsed LayoutConfig
        """
        try:
            # Try to extract JSON from LLM response
            response_data = self._extract_json_from_response(llm_response)
            
            # Map LLM analysis to LayoutConfig fields
            config = LayoutConfig(
                user_id=user_id,
                section_order_preference=response_data.get("section_order", "standard"),
                header_style=response_data.get("header_style", "name-contact"),
                contact_info_placement=response_data.get("contact_placement", "top-center"),
                summary_section_preference=response_data.get("summary_style", "brief"),
                skills_section_format=response_data.get("skills_format", "categorized"),
                experience_date_format=response_data.get("date_format", "month-year"),
                bullet_point_style=response_data.get("bullet_style", "consistent"),
                spacing_preferences=response_data.get("spacing", {}),
                font_style_preferences=response_data.get("font_preferences", {}),
                length_preferences=response_data.get("length_preferences", {}),
                section_emphasis=response_data.get("section_emphasis", {}),
                is_active=True
            )
            
            return config
            
        except Exception as e:
            logger.warning(f"Failed to parse layout response, using default config: {e}")
            # Return default config if parsing fails
            return LayoutConfig(
                user_id=user_id,
                section_order_preference="standard",
                header_style="name-contact",
                is_active=True
            )

    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extract JSON data from LLM response.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed JSON data
        """
        try:
            # Look for JSON block in response
            start_markers = ["{", "```json", "```"]
            end_markers = ["}", "```"]
            
            json_start = -1
            json_end = -1
            
            for marker in start_markers:
                pos = response.find(marker)
                if pos != -1 and (json_start == -1 or pos < json_start):
                    json_start = pos
            
            if json_start == -1:
                # No JSON found, create from key-value pairs
                return self._parse_key_value_response(response)
            
            # Find end of JSON
            brace_count = 0
            in_json = False
            
            for i, char in enumerate(response[json_start:]):
                if char == '{':
                    brace_count += 1
                    in_json = True
                elif char == '}':
                    brace_count -= 1
                    if in_json and brace_count == 0:
                        json_end = json_start + i + 1
                        break
            
            if json_end == -1:
                json_end = len(response)
            
            json_str = response[json_start:json_end]
            
            # Clean up JSON string
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            return json.loads(json_str)
            
        except Exception as e:
            logger.warning(f"Failed to extract JSON from response: {e}")
            return self._parse_key_value_response(response)

    def _parse_key_value_response(self, response: str) -> Dict[str, Any]:
        """
        Parse key-value pairs from unstructured response.
        
        Args:
            response: Raw response text
            
        Returns:
            Parsed data dictionary
        """
        data = {}
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                
                # Convert common values
                if value.lower() in ['true', 'yes']:
                    value = True
                elif value.lower() in ['false', 'no']:
                    value = False
                elif value.startswith('[') and value.endswith(']'):
                    try:
                        value = json.loads(value)
                    except:
                        value = value[1:-1].split(',')
                
                data[key] = value
        
        return data

    def _calculate_confidence_score(self, text: str) -> float:
        """
        Calculate confidence score for extracted text.
        
        Args:
            text: Extracted text content
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        try:
            # Base score on text characteristics
            word_count = len(text.split())
            
            # Length factor
            length_score = min(1.0, word_count / 300)  # 300 words = full score
            
            # Completeness factor (presence of key sections)
            key_indicators = [
                "experience", "education", "skills", "summary", "objective",
                "contact", "work", "employment", "university", "degree"
            ]
            
            found_indicators = sum(1 for indicator in key_indicators 
                                 if indicator.lower() in text.lower())
            completeness_score = min(1.0, found_indicators / 5)  # 5 indicators = full score
            
            # Text quality factor (avoid too many special characters/formatting)
            special_char_ratio = sum(1 for char in text if not char.isalnum() and char not in ' \n\t.,!?-') / len(text)
            quality_score = max(0.0, 1.0 - special_char_ratio * 2)  # Penalize excessive special chars
            
            # Combine factors
            confidence = (length_score * 0.4 + completeness_score * 0.4 + quality_score * 0.2)
            
            return round(confidence, 2)
            
        except Exception:
            return 0.5  # Default confidence if calculation fails