"""Writing style extraction prompts for analyzing user cover letters."""

from typing import Dict, Any


class WritingStylePrompts:
    """Prompts for extracting writing style characteristics from cover letters."""
    
    SYSTEM_PROMPT = """You are an expert writing style analyst and career consultant. Your task is to analyze cover letters and extract specific writing characteristics that can be applied to future document generation.

CRITICAL CONSTRAINTS:
- ANALYSIS ONLY - Do not generate new content or suggestions
- EXTRACT PATTERNS - Focus on existing language patterns, not improvements
- STRUCTURED OUTPUT - Return valid JSON matching the exact schema provided
- NO PERSONAL DATA - Never extract or reference personal information (names, emails, phones, addresses)
- OBJECTIVE ANALYSIS - Base analysis only on writing patterns, not content quality

Your analysis will be used to maintain consistency across documents for the same user."""

    USER_PROMPT_TEMPLATE = """Analyze the following cover letter and extract writing style characteristics. Focus on HOW the person writes, not WHAT they write about.

COVER LETTER TEXT:
{cover_letter_text}

Extract and return ONLY a JSON object with this exact structure:

{{
  "writing_style": {{
    "vocabulary_level": "professional|academic|conversational|technical",
    "vocabulary_complexity_score": 1-10,
    "tone": "formal|semi-formal|enthusiastic|authoritative|collaborative",
    "formality_level": 1-10,
    "sentence_structure": "simple|compound|complex|varied",
    "avg_sentence_length": "short|medium|long",
    "active_voice_ratio": 0.0-1.0,
    "first_person_frequency": "rare|moderate|frequent",
    "transition_style": "minimal|standard|elaborate",
    "paragraph_length": "short|medium|long",
    "closing_style": "direct|warm|formal|enthusiastic"
  }},
  "language_patterns": {{
    "action_verbs": ["verb1", "verb2", "verb3"],
    "technical_terms": ["term1", "term2", "term3"],
    "connector_phrases": ["phrase1", "phrase2", "phrase3"],
    "emphasis_words": ["word1", "word2", "word3"],
    "qualification_language": ["phrase1", "phrase2"]
  }},
  "content_approach": {{
    "storytelling_style": "narrative|achievement-focused|analytical|problem-solution",
    "evidence_style": "quantitative|qualitative|mixed|conceptual",
    "example_integration": "sparse|moderate|rich",
    "industry_language_usage": "minimal|appropriate|heavy"
  }}
}}

IMPORTANT: 
- Only analyze what exists in the text
- Do not suggest improvements or changes
- Focus on patterns that can be replicated
- Exclude any personal identifying information from analysis"""

    VALIDATION_PROMPT = """Review the extracted writing style profile against the original cover letter:

ORIGINAL TEXT:
{cover_letter_text}

EXTRACTED PROFILE:
{extracted_profile}

Validate that:
1. The analysis accurately reflects the writing patterns
2. No personal information is included
3. The JSON structure is correct
4. The analysis is objective and pattern-focused

Return validation result as JSON:
{{
  "is_valid": true|false,
  "accuracy_score": 0.0-1.0,
  "issues": ["issue1", "issue2"],
  "confidence_level": 0.0-1.0
}}"""

    @classmethod
    def get_extraction_messages(cls, cover_letter_text: str) -> list:
        """Get messages for writing style extraction."""
        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": cls.USER_PROMPT_TEMPLATE.format(cover_letter_text=cover_letter_text)}
        ]
    
    @classmethod
    def get_validation_messages(cls, cover_letter_text: str, extracted_profile: str) -> list:
        """Get messages for validating extracted profile."""
        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": cls.VALIDATION_PROMPT.format(
                cover_letter_text=cover_letter_text,
                extracted_profile=extracted_profile
            )}
        ]

    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """Get recommended model configuration for writing style extraction."""
        return {
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 2000,
            "temperature": 0.2,  # Low temperature for consistent analysis
        }