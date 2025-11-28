"""
Prompt Service - Source code-based prompt templates (V3.0).
"""

import logging
from typing import Dict, Any, Optional
from jinja2 import Environment

logger = logging.getLogger(__name__)


class PromptService:
    """Service for managing and rendering prompt templates."""
    
    def __init__(self):
        """Initialize the prompt service."""
        self.env = Environment()
    
    def render(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Render a prompt template with variables."""
        
        # Cover letter generation template
        if template_name == "cover_letter_generation":
            template_str = """You are an expert cover letter writer.

Write a compelling, personalized cover letter for this job:

**Job Details:**
- Position: {{ job_title }}
- Company: {{ job_company }}  
- Description: {{ job_description }}

**Candidate:**
- Name: {{ user_name }}
- Email: {{ user_email }}
- Summary: {{ professional_summary }}

**Top Experiences:**
{% for exp in top_experiences %}
• {{ exp.title }} at {{ exp.company }}
  {{ exp.enhanced_description or exp.description }}
{% endfor %}

**Top Projects:**
{% for proj in top_projects %}
• {{ proj.name }}
  {{ proj.enhanced_description or proj.description }}
{% endfor %}

**Key Skills:** {{ top_skills | join(', ') }}

**Writing Style:**
- Level: {{ writing_style.writing_style.vocabulary_level }}
- Tone: {{ writing_style.writing_style.tone }}
- Formality: {{ writing_style.writing_style.formality_level }}/10

{% if user_custom_prompt %}
**Additional Instructions:** {{ user_custom_prompt }}
{% endif %}

Requirements:
1. Use ONLY provided information - no fabrication
2. Match the writing style and tone
3. Include relevant job keywords naturally
4. Keep concise (300-400 words)
5. Professional greeting and closing

Write the complete cover letter:"""

        # Content ranking template
        elif template_name == "content_ranking":
            template_str = """Rank the candidate's content by relevance to this job.

**Job:** {{ job_title }} at {{ job_company }}
**Description:** {{ job_description }}

**Experiences:**
{% for exp in experiences %}
{{ loop.index }}. ID: {{ exp.id }}
   {{ exp.title }} at {{ exp.company }}
   {{ exp.enhanced_description or exp.description }}
{% endfor %}

**Projects:**
{% for proj in projects %}
{{ loop.index }}. ID: {{ proj.id }}
   {{ proj.name }}
   {{ proj.enhanced_description or proj.description }}
{% endfor %}

{% if user_custom_prompt %}
**Instructions:** {{ user_custom_prompt }}
{% endif %}

Return JSON with ranked IDs and analysis:
{
  "ranked_experience_ids": ["most_relevant_first", "..."],
  "ranked_project_ids": ["most_relevant_first", "..."],
  "ranking_rationale": "Your explanation...",
  "keyword_matches": {"Python": 3, "ML": 2},
  "relevance_scores": {"exp_id": 0.95, "proj_id": 0.87}
}"""

        # Profile enhancement template  
        elif template_name == "profile_enhancement":
            template_str = """Enhance this summary to match the writing style.

**Original:** {{ original_summary }}

**Style Reference:** {{ sample_text }}

**Style Analysis:**
- Level: {{ writing_style.writing_style.vocabulary_level }}
- Tone: {{ writing_style.writing_style.tone }}
- Formality: {{ writing_style.writing_style.formality_level }}/10

Requirements:
1. Preserve all facts
2. Match the style and tone
3. Use similar vocabulary level
4. Keep similar length

Enhanced summary:"""

        else:
            raise KeyError(f"Unknown template: {template_name}")
        
        # Render the template
        template = self.env.from_string(template_str)
        return template.render(**variables)


# FastAPI dependency
def get_prompt_service() -> PromptService:
    """Get prompt service instance."""
    return PromptService()
