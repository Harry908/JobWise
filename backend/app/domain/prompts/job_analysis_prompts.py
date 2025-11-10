"""Job analysis prompts for parsing and analyzing job postings."""

from typing import Dict, Any


class JobAnalysisPrompts:
    """Prompts for analyzing job postings to extract requirements and keywords."""
    
    SYSTEM_PROMPT = """You are an expert job market analyst and requirements extraction specialist. Your task is to analyze job postings and extract key requirements, skills, and qualifications that can be used for resume tailoring.

CRITICAL CONSTRAINTS:
- ANALYSIS ONLY - Extract only what is explicitly mentioned in the job posting
- NO ASSUMPTIONS - Do not infer requirements that aren't clearly stated
- STRUCTURED OUTPUT - Return valid JSON matching the exact schema provided
- FACTUAL EXTRACTION - Base analysis only on the job posting content
- KEYWORD FOCUS - Identify specific terms and phrases used in the posting

Your analysis will be used to tailor resumes and cover letters to match job requirements."""

    USER_PROMPT_TEMPLATE = """Analyze the following job posting and extract key requirements and characteristics:

JOB POSTING:
Title: {job_title}
Company: {company_name}
Location: {job_location}
Description:
{job_description}

Extract and return ONLY a JSON object with this exact structure:

{{
  "job_basics": {{
    "title": "{job_title}",
    "company": "{company_name}",
    "location": "{job_location}",
    "employment_type": "full-time|part-time|contract|internship|temporary",
    "seniority_level": "entry|mid|senior|lead|executive",
    "industry_sector": "technology|finance|healthcare|education|etc"
  }},
  "technical_requirements": {{
    "required_skills": ["skill1", "skill2", "skill3"],
    "preferred_skills": ["skill1", "skill2", "skill3"],
    "programming_languages": ["language1", "language2"],
    "technologies": ["tech1", "tech2", "tech3"],
    "tools_software": ["tool1", "tool2", "tool3"],
    "frameworks": ["framework1", "framework2"]
  }},
  "experience_requirements": {{
    "years_required": {{
      "min": 0,
      "max": 10,
      "preferred": 3
    }},
    "specific_experience": ["experience1", "experience2"],
    "industry_experience": ["industry1", "industry2"],
    "role_types": ["role1", "role2"]
  }},
  "education_requirements": {{
    "degree_required": true|false,
    "degree_level": "associates|bachelors|masters|phd|none",
    "preferred_majors": ["major1", "major2"],
    "certifications": ["cert1", "cert2"],
    "equivalent_experience": true|false
  }},
  "key_responsibilities": {{
    "primary_duties": ["duty1", "duty2", "duty3"],
    "leadership_aspects": ["aspect1", "aspect2"],
    "collaboration_needs": ["need1", "need2"],
    "project_types": ["type1", "type2"]
  }},
  "soft_skills": {{
    "communication": ["skill1", "skill2"],
    "problem_solving": ["skill1", "skill2"],
    "teamwork": ["skill1", "skill2"],
    "leadership": ["skill1", "skill2"],
    "other": ["skill1", "skill2"]
  }},
  "keywords_for_matching": {{
    "high_priority": ["keyword1", "keyword2", "keyword3"],
    "medium_priority": ["keyword4", "keyword5", "keyword6"],
    "industry_terms": ["term1", "term2", "term3"],
    "action_verbs": ["verb1", "verb2", "verb3"]
  }},
  "company_culture": {{
    "values_mentioned": ["value1", "value2"],
    "work_environment": "collaborative|independent|hybrid|fast-paced|structured",
    "growth_opportunities": ["opportunity1", "opportunity2"],
    "benefits_highlights": ["benefit1", "benefit2"]
  }}
}}

IMPORTANT:
- Only extract information explicitly mentioned in the job posting
- Use exact terms and phrases from the posting when possible
- Categorize skills as required vs preferred based on language used
- Identify the most important keywords for ATS optimization"""

    KEYWORD_OPTIMIZATION_PROMPT = """Analyze the job posting for ATS (Applicant Tracking System) optimization keywords:

JOB POSTING:
{job_description}

Focus on identifying keywords and phrases that are likely to be searched by ATS systems:

{{
  "ats_keywords": {{
    "must_have_terms": ["term1", "term2", "term3"],
    "skill_variations": {{
      "JavaScript": ["JS", "Javascript", "ECMAScript"],
      "skill_name": ["variation1", "variation2"]
    }},
    "acronym_expansions": {{
      "API": "Application Programming Interface",
      "acronym": "full_expansion"
    }},
    "keyword_density_targets": {{
      "keyword1": 3,
      "keyword2": 2
    }},
    "phrase_matching": ["exact phrase1", "exact phrase2"],
    "industry_buzzwords": ["buzzword1", "buzzword2"]
  }},
  "optimization_strategy": {{
    "primary_focus": ["focus1", "focus2"],
    "secondary_focus": ["focus3", "focus4"],
    "avoid_over_optimization": ["term1", "term2"]
  }}
}}"""

    @classmethod
    def get_analysis_messages(cls, job_title: str, company_name: str, job_location: str, job_description: str) -> list:
        """Get messages for job analysis extraction."""
        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": cls.USER_PROMPT_TEMPLATE.format(
                job_title=job_title,
                company_name=company_name,
                job_location=job_location,
                job_description=job_description
            )}
        ]
    
    @classmethod
    def get_keyword_optimization_messages(cls, job_description: str) -> list:
        """Get messages for ATS keyword optimization analysis."""
        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": cls.KEYWORD_OPTIMIZATION_PROMPT.format(job_description=job_description)}
        ]

    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """Get recommended model configuration for job analysis."""
        return {
            "model": "llama-3.1-8b-instant",  # Fast model for analysis
            "max_tokens": 2500,
            "temperature": 0.1,  # Very low temperature for factual extraction
        }