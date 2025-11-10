"""Structural analysis prompts for analyzing resume layout and formatting preferences."""

from typing import Dict, Any


class StructuralAnalysisPrompts:
    """Prompts for extracting structural and layout preferences from example resumes."""
    
    SYSTEM_PROMPT = """You are an expert resume structure analyst and document formatting specialist. Your task is to analyze example resumes and extract specific layout, formatting, and structural characteristics.

CRITICAL CONSTRAINTS:
- STRUCTURE ANALYSIS ONLY - Focus on HOW content is organized, not WHAT the content is
- EXTRACT PATTERNS - Identify layout preferences, section order, formatting styles
- STRUCTURED OUTPUT - Return valid JSON matching the exact schema provided
- NO PERSONAL DATA - Never extract or reference personal information from resumes
- OBJECTIVE ANALYSIS - Focus on structural patterns and formatting choices

Your analysis will be used to replicate the same structural approach for future resumes."""

    USER_PROMPT_TEMPLATE = """Analyze the following resume and extract structural and formatting characteristics. Focus on the layout, organization, and presentation style.

RESUME TEXT:
{resume_text}

Extract and return ONLY a JSON object with this exact structure:

{{
  "layout_preferences": {{
    "section_order": ["section1", "section2", "section3"],
    "header_style": "centered|left-aligned|two-column|contact-block",
    "date_format": "MM/YYYY|MM/DD/YYYY|Month YYYY|YYYY",
    "location_display": "city-state|full-address|city-only|remote",
    "bullet_style": "standard|achievement|CAR|STAR|numeric"
  }},
  "content_density": {{
    "bullets_per_experience": {{
      "min": 1,
      "max": 6,
      "preferred": 3
    }},
    "line_spacing": "tight|standard|loose",
    "section_spacing": "minimal|standard|generous",
    "white_space_usage": "minimal|balanced|generous"
  }},
  "formatting_patterns": {{
    "emphasis_style": "bold|italic|caps|underlining",
    "title_formatting": "bold|caps|italic|standard",
    "company_formatting": "bold|italic|standard",
    "skill_grouping": "categorized|listed|integrated|highlighted",
    "contact_integration": "header|sidebar|footer|inline"
  }},
  "section_characteristics": {{
    "summary_style": "paragraph|bullets|objectives|none",
    "experience_focus": "responsibilities|achievements|mixed|skills",
    "education_detail_level": "minimal|standard|detailed|academic",
    "skills_presentation": "categorized|listed|integrated|proficiency",
    "project_integration": "separate|embedded|portfolio|minimal"
  }},
  "professional_polish": {{
    "consistency_level": "basic|good|excellent",
    "ats_optimization": "minimal|moderate|high",
    "readability_score": 1-10,
    "visual_hierarchy": "poor|good|excellent"
  }}
}}

IMPORTANT:
- Focus only on structure and formatting patterns
- Ignore specific content details and personal information
- Analyze how sections are organized and presented
- Note consistent formatting choices throughout the document"""

    CONSISTENCY_ANALYSIS_PROMPT = """Compare multiple resume examples to identify consistent structural preferences:

RESUME EXAMPLES:
{resume_examples}

Analyze patterns across all examples and return:
{{
  "consistent_patterns": {{
    "common_section_order": ["section1", "section2"],
    "consistent_formatting": ["pattern1", "pattern2"],
    "preferred_styles": ["style1", "style2"]
  }},
  "variations": {{
    "inconsistent_elements": ["element1", "element2"],
    "context_dependent": ["when_X_then_Y"]
  }},
  "confidence_score": 0.0-1.0,
  "recommendation": "use_most_common|blend_approaches|require_user_selection"
}}"""

    VALIDATION_PROMPT = """Review the extracted structural profile against the original resume:

ORIGINAL RESUME:
{resume_text}

EXTRACTED PROFILE:
{extracted_profile}

Validate that:
1. The structural analysis accurately reflects the resume layout
2. No personal information is included in the analysis
3. The formatting patterns are correctly identified
4. The JSON structure is complete and valid

Return validation result as JSON:
{{
  "is_valid": true|false,
  "structural_accuracy": 0.0-1.0,
  "formatting_accuracy": 0.0-1.0,
  "issues": ["issue1", "issue2"],
  "missing_elements": ["element1", "element2"],
  "confidence_level": 0.0-1.0
}}"""

    @classmethod
    def get_extraction_messages(cls, resume_text: str) -> list:
        """Get messages for structural analysis extraction."""
        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": cls.USER_PROMPT_TEMPLATE.format(resume_text=resume_text)}
        ]
    
    @classmethod
    def get_consistency_messages(cls, resume_examples: str) -> list:
        """Get messages for analyzing consistency across multiple resumes."""
        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": cls.CONSISTENCY_ANALYSIS_PROMPT.format(resume_examples=resume_examples)}
        ]
    
    @classmethod
    def get_validation_messages(cls, resume_text: str, extracted_profile: str) -> list:
        """Get messages for validating extracted structural profile."""
        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": cls.VALIDATION_PROMPT.format(
                resume_text=resume_text,
                extracted_profile=extracted_profile
            )}
        ]

    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """Get recommended model configuration for structural analysis."""
        return {
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 2500,
            "temperature": 0.2,  # Low temperature for consistent analysis
        }