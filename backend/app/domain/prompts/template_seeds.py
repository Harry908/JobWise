"""
Jinja2 Prompt Templates for V3.0 System.

These templates are seeded into the prompt_templates table on initialization.
Uses Jinja2 syntax for variable substitution and logic.
"""

from typing import Dict, List
import uuid
from datetime import datetime


# Template 1: Writing Style Extraction (in-memory, no LLM call)
WRITING_STYLE_EXTRACTION_TEMPLATE = """Analyzing writing style from sample cover letter...

Sample Text:
{{ sample_text }}

INSTRUCTIONS:
Extract the following writing characteristics:
1. Vocabulary level and complexity (1-10 scale)
2. Tone and formality (1-10 scale)
3. Sentence structure patterns
4. Action verbs and technical terms used
5. Transition phrases and connector words

ANTI-FABRICATION RULE: Only extract patterns that appear in the provided text. Do not invent or assume characteristics.

Return JSON format with these exact keys:
{
  "writing_style": {
    "vocabulary_level": "professional|academic|conversational",
    "vocabulary_complexity_score": 1-10,
    "tone": "formal|semi-formal|enthusiastic|authoritative",
    "formality_level": 1-10,
    "sentence_structure": "simple|compound|complex|varied",
    "avg_sentence_length": "short|medium|long",
    "active_voice_ratio": 0.0-1.0,
    "first_person_frequency": "rare|moderate|frequent"
  },
  "language_patterns": {
    "action_verbs": ["verb1", "verb2", ...],
    "technical_terms": ["term1", "term2", ...],
    "connector_phrases": ["phrase1", "phrase2", ...]
  }
}"""

# Template 2: Profile Enhancement (llama-3.3-70b-versatile)
PROFILE_ENHANCEMENT_TEMPLATE = """You are an expert resume writer tasked with enhancing a professional summary and experience descriptions.

ORIGINAL PROFESSIONAL SUMMARY:
{{ professional_summary }}

{% if experiences %}
ORIGINAL WORK EXPERIENCES:
{% for exp in experiences %}
{{ loop.index }}. {{ exp.title }} at {{ exp.company }} ({{ exp.start_date }} - {{ exp.end_date }})
Original Description: {{ exp.description }}
{% endfor %}
{% endif %}

{% if projects %}
ORIGINAL PROJECTS:
{% for proj in projects %}
{{ loop.index }}. {{ proj.name }}
Original Description: {{ proj.description }}
Technologies: {{ proj.technologies|join(', ') }}
{% endfor %}
{% endif %}

ENHANCEMENT GUIDELINES:
1. Use strong action verbs (achieved, spearheaded, architected, optimized)
2. Add quantifiable metrics where applicable (e.g., "increased by X%", "reduced by Y hours")
3. Emphasize technical depth and business impact
4. Maintain professional tone
5. Keep descriptions concise (2-3 sentences per experience)

ANTI-FABRICATION RULES:
- DO NOT invent metrics, technologies, or achievements
- DO NOT add companies, dates, or projects not in the original
- DO NOT fabricate specific numbers or percentages
- ONLY enhance wording and structure of existing content
- If metrics are missing, use qualitative descriptors like "significantly improved" instead of inventing numbers

Return JSON format:
{
  "enhanced_professional_summary": "enhanced text here",
  "enhanced_experiences": [
    {
      "experience_id": "uuid from input",
      "enhanced_description": "enhanced text here"
    }
  ],
  "enhanced_projects": [
    {
      "project_id": "uuid from input",
      "enhanced_description": "enhanced text here"
    }
  ]
}"""

# Template 3: Content Ranking (llama-3.1-8b-instant)
CONTENT_RANKING_TEMPLATE = """You are an expert at analyzing job descriptions and ranking resume content by relevance.

JOB DESCRIPTION:
Title: {{ job_title }}
Company: {{ job_company }}
Description: {{ job_description }}

USER PROFILE CONTENT TO RANK:

EXPERIENCES:
{% for exp in experiences %}
ID: {{ exp.id }}
Title: {{ exp.title }}
Company: {{ exp.company }}
Description: {{ exp.description }}
---
{% endfor %}

PROJECTS:
{% for proj in projects %}
ID: {{ proj.id }}
Name: {{ proj.name }}
Description: {{ proj.description }}
Technologies: {{ proj.technologies|join(', ') }}
---
{% endfor %}

SKILLS:
{% for skill_category, skills in skills.items() %}
Category: {{ skill_category }}
Skills: {{ skills|join(', ') }}
---
{% endfor %}

RANKING INSTRUCTIONS:
1. Rank experiences by relevance to job requirements (most relevant first)
2. Rank projects by technical alignment with job
3. Rank skills by job description keyword matches
4. Provide brief explanation for top 3 ranked items in each category

Return JSON format:
{
  "ranked_experience_ids": ["uuid1", "uuid2", "uuid3", ...],
  "ranked_project_ids": ["uuid1", "uuid2", ...],
  "ranked_skill_ids": ["skill1", "skill2", ...],
  "ranking_confidence_score": 0.0-1.0,
  "ranking_explanations": {
    "uuid1": "explanation why this is most relevant",
    "uuid2": "explanation for second most relevant"
  }
}"""

# Template 4: Cover Letter Generation (llama-3.3-70b-versatile)
COVER_LETTER_GENERATION_TEMPLATE = """You are an expert cover letter writer. Generate a professional cover letter using the user's writing style.

WRITING STYLE TO MATCH:
{{ writing_style_json }}

JOB INFORMATION:
Title: {{ job_title }}
Company: {{ job_company }}
Description: {{ job_description }}

USER PROFILE:
Name: {{ user_name }}
Professional Summary: {{ professional_summary }}
Top Experiences: {{ top_experiences }}
Top Projects: {{ top_projects }}
Key Skills: {{ key_skills }}

{% if user_custom_prompt %}
USER CUSTOM INSTRUCTIONS:
{{ user_custom_prompt }}
{% endif %}

GENERATION GUIDELINES:
1. Match the writing style extracted from user's sample (tone, vocabulary, sentence structure)
2. Address the specific job requirements mentioned in the description
3. Highlight 2-3 most relevant experiences or projects
4. Use quantifiable achievements from the profile
5. Keep length to {{ word_limit|default(300) }} words
6. Professional greeting and closing

ANTI-FABRICATION RULES:
- ONLY use information from the user profile provided
- DO NOT invent job titles, companies, dates, or achievements
- DO NOT add experiences or projects not in the profile
- DO NOT fabricate specific metrics or numbers
- If specific details are missing, use general qualitative descriptions

STRUCTURE:
1. Header with contact info
2. Greeting
3. Opening paragraph (interest + brief qualification)
4. Body paragraph (relevant experience + skills)
5. Closing paragraph (enthusiasm + call to action)
6. Professional sign-off

Return the complete cover letter as plain text (no JSON).
"""


def get_template_seeds() -> List[Dict]:
    """
    Get initial prompt templates for database seeding.
    
    Returns:
        List of template dictionaries ready for database insertion
    """
    now = datetime.utcnow().isoformat()
    
    return [
        {
            "id": str(uuid.uuid4()),
            "template_name": "writing_style_extraction",
            "version": "1.0.0",
            "is_active": True,
            "template_content": WRITING_STYLE_EXTRACTION_TEMPLATE.strip(),
            "required_variables": ["sample_text"],
            "optional_variables": {},
            "description": "Extract writing style patterns from sample cover letter (in-memory analysis)",
            "expected_output_format": "json",
            "estimated_tokens": 400,
            "ab_test_group": None,
            "performance_metrics": {},
            "deprecated_at": None,
            "superseded_by_template_id": None,
            "created_at": now,
            "updated_at": now,
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "template_name": "profile_enhancement",
            "version": "1.0.0",
            "is_active": True,
            "template_content": PROFILE_ENHANCEMENT_TEMPLATE.strip(),
            "required_variables": ["professional_summary"],
            "optional_variables": {"experiences": [], "projects": []},
            "description": "AI-powered enhancement of professional summary and experience descriptions",
            "expected_output_format": "json",
            "estimated_tokens": 600,
            "ab_test_group": None,
            "performance_metrics": {},
            "deprecated_at": None,
            "superseded_by_template_id": None,
            "created_at": now,
            "updated_at": now,
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "template_name": "content_ranking",
            "version": "1.0.0",
            "is_active": True,
            "template_content": CONTENT_RANKING_TEMPLATE.strip(),
            "required_variables": ["job_title", "job_company", "job_description", "experiences", "projects", "skills"],
            "optional_variables": {},
            "description": "Rank resume content by relevance to specific job posting",
            "expected_output_format": "json",
            "estimated_tokens": 500,
            "ab_test_group": None,
            "performance_metrics": {},
            "deprecated_at": None,
            "superseded_by_template_id": None,
            "created_at": now,
            "updated_at": now,
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "template_name": "cover_letter_generation",
            "version": "1.0.0",
            "is_active": True,
            "template_content": COVER_LETTER_GENERATION_TEMPLATE.strip(),
            "required_variables": [
                "writing_style_json",
                "job_title",
                "job_company",
                "job_description",
                "user_name",
                "professional_summary",
                "top_experiences",
                "top_projects",
                "key_skills"
            ],
            "optional_variables": {"user_custom_prompt": None, "word_limit": 300},
            "description": "Generate personalized cover letter matching user's writing style",
            "expected_output_format": "plain_text",
            "estimated_tokens": 800,
            "ab_test_group": None,
            "performance_metrics": {},
            "deprecated_at": None,
            "superseded_by_template_id": None,
            "created_at": now,
            "updated_at": now,
            "created_by": "system"
        }
    ]
