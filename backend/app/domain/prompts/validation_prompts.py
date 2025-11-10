"""Quality validation prompts for analyzing generated content against user examples."""

from typing import Dict, Any


class ValidationPrompts:
    """Prompts for validating generated content quality against user examples and preferences."""
    
    SYSTEM_PROMPT = """You are an expert document quality analyst specializing in resume and cover letter evaluation. Your task is to validate generated documents against user examples and preferences to ensure consistency, quality, and alignment.

CRITICAL CONSTRAINTS:
- OBJECTIVE ANALYSIS - Provide factual, measurable assessments
- COMPARISON FOCUS - Evaluate how well generated content matches user examples
- STRUCTURED FEEDBACK - Return specific, actionable recommendations
- QUALITY METRICS - Provide quantitative scores for different aspects
- NO CONTENT CREATION - Only analyze and validate existing content

You will assess consistency, style alignment, structural accuracy, and professional quality."""

    CONSISTENCY_VALIDATION_PROMPT = """Compare the generated document with the user's example documents to validate consistency:

GENERATED DOCUMENT:
{generated_content}

USER EXAMPLE DOCUMENTS:
{example_documents}

USER WRITING STYLE PREFERENCES:
{writing_style_preferences}

USER STRUCTURAL PREFERENCES:
{structural_preferences}

Analyze and return a detailed validation report as JSON:

{{
  "overall_consistency_score": 0.0-1.0,
  "writing_style_analysis": {{
    "vocabulary_consistency": 0.0-1.0,
    "tone_alignment": 0.0-1.0,
    "sentence_structure_match": 0.0-1.0,
    "voice_authenticity": 0.0-1.0,
    "specific_deviations": ["deviation1", "deviation2"]
  }},
  "structural_analysis": {{
    "layout_consistency": 0.0-1.0,
    "section_order_match": 0.0-1.0,
    "formatting_alignment": 0.0-1.0,
    "bullet_style_consistency": 0.0-1.0,
    "structural_deviations": ["deviation1", "deviation2"]
  }},
  "professional_quality": {{
    "grammar_accuracy": 0.0-1.0,
    "clarity_score": 0.0-1.0,
    "coherence_score": 0.0-1.0,
    "professional_polish": 0.0-1.0,
    "ats_optimization": 0.0-1.0
  }},
  "improvement_recommendations": [
    {{
      "category": "writing_style|structure|quality",
      "issue": "specific issue identified",
      "recommendation": "specific improvement suggestion",
      "priority": "high|medium|low"
    }}
  ],
  "validation_summary": {{
    "meets_standards": true|false,
    "confidence_level": 0.0-1.0,
    "key_strengths": ["strength1", "strength2"],
    "key_weaknesses": ["weakness1", "weakness2"]
  }}
}}"""

    ATS_OPTIMIZATION_PROMPT = """Evaluate the generated document for ATS (Applicant Tracking System) optimization:

GENERATED DOCUMENT:
{generated_content}

TARGET JOB REQUIREMENTS:
{job_requirements}

ATS BEST PRACTICES:
{ats_guidelines}

Analyze and return ATS optimization assessment:

{{
  "ats_score": 0.0-1.0,
  "keyword_analysis": {{
    "required_keywords_found": ["keyword1", "keyword2"],
    "required_keywords_missing": ["keyword3", "keyword4"],
    "keyword_density_analysis": {{
      "keyword1": {{"count": 3, "optimal_range": "2-4", "status": "optimal"}},
      "keyword2": {{"count": 1, "optimal_range": "2-3", "status": "under_optimized"}}
    }},
    "keyword_integration_quality": 0.0-1.0
  }},
  "format_compatibility": {{
    "section_header_clarity": 0.0-1.0,
    "bullet_point_formatting": 0.0-1.0,
    "date_format_consistency": 0.0-1.0,
    "contact_info_accessibility": 0.0-1.0
  }},
  "content_structure": {{
    "section_order_optimization": 0.0-1.0,
    "content_hierarchy_clarity": 0.0-1.0,
    "experience_presentation": 0.0-1.0,
    "skills_accessibility": 0.0-1.0
  }},
  "ats_recommendations": [
    {{
      "category": "keywords|formatting|structure",
      "issue": "specific ATS issue",
      "recommendation": "specific improvement",
      "impact": "high|medium|low"
    }}
  ]
}}"""

    CONTENT_ACCURACY_PROMPT = """Validate that the generated content accurately represents the user's profile without fabrication:

GENERATED DOCUMENT:
{generated_content}

USER PROFILE DATA:
{user_profile}

Check for accuracy and authenticity:

{{
  "accuracy_score": 0.0-1.0,
  "content_verification": {{
    "experiences_accuracy": 0.0-1.0,
    "skills_accuracy": 0.0-1.0,
    "education_accuracy": 0.0-1.0,
    "achievements_accuracy": 0.0-1.0
  }},
  "fabrication_check": {{
    "potential_fabrications": ["item1", "item2"],
    "exaggerations_detected": ["item1", "item2"],
    "missing_disclaimers": ["item1", "item2"]
  }},
  "authenticity_assessment": {{
    "tone_authenticity": 0.0-1.0,
    "voice_consistency": 0.0-1.0,
    "experience_representation": 0.0-1.0
  }},
  "accuracy_issues": [
    {{
      "type": "fabrication|exaggeration|misrepresentation",
      "content": "problematic content",
      "source_mismatch": "what should it be based on",
      "severity": "high|medium|low"
    }}
  ]
}}"""

    QUALITY_AUDIT_PROMPT = """Perform a comprehensive quality audit of the generated document:

GENERATED DOCUMENT:
{generated_content}

QUALITY CRITERIA:
{quality_standards}

Conduct thorough quality assessment:

{{
  "overall_quality_score": 0.0-1.0,
  "quality_dimensions": {{
    "content_quality": 0.0-1.0,
    "presentation_quality": 0.0-1.0,
    "professional_impact": 0.0-1.0,
    "target_alignment": 0.0-1.0
  }},
  "detailed_analysis": {{
    "strengths": ["strength1", "strength2", "strength3"],
    "weaknesses": ["weakness1", "weakness2"],
    "improvement_opportunities": ["opportunity1", "opportunity2"],
    "risk_factors": ["risk1", "risk2"]
  }},
  "competitive_readiness": {{
    "market_competitiveness": 0.0-1.0,
    "differentiation_factors": ["factor1", "factor2"],
    "improvement_potential": 0.0-1.0
  }},
  "final_recommendations": [
    {{
      "priority": "critical|high|medium|low",
      "category": "content|structure|style|optimization",
      "recommendation": "specific action to take",
      "expected_impact": "description of improvement"
    }}
  ]
}}"""

    @classmethod
    def get_consistency_validation_messages(
        cls,
        generated_content: str,
        example_documents: str,
        writing_style_preferences: str,
        structural_preferences: str
    ) -> list:
        """Get messages for consistency validation."""
        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": cls.CONSISTENCY_VALIDATION_PROMPT.format(
                generated_content=generated_content,
                example_documents=example_documents,
                writing_style_preferences=writing_style_preferences,
                structural_preferences=structural_preferences
            )}
        ]
    
    @classmethod
    def get_ats_optimization_messages(
        cls,
        generated_content: str,
        job_requirements: str,
        ats_guidelines: str
    ) -> list:
        """Get messages for ATS optimization validation."""
        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": cls.ATS_OPTIMIZATION_PROMPT.format(
                generated_content=generated_content,
                job_requirements=job_requirements,
                ats_guidelines=ats_guidelines
            )}
        ]
    
    @classmethod
    def get_accuracy_validation_messages(
        cls,
        generated_content: str,
        user_profile: str
    ) -> list:
        """Get messages for content accuracy validation."""
        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": cls.CONTENT_ACCURACY_PROMPT.format(
                generated_content=generated_content,
                user_profile=user_profile
            )}
        ]
    
    @classmethod
    def get_quality_audit_messages(
        cls,
        generated_content: str,
        quality_standards: str
    ) -> list:
        """Get messages for comprehensive quality audit."""
        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": cls.QUALITY_AUDIT_PROMPT.format(
                generated_content=generated_content,
                quality_standards=quality_standards
            )}
        ]

    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """Get recommended model configuration for validation."""
        return {
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 2500,
            "temperature": 0.2,  # Low temperature for consistent analysis
        }