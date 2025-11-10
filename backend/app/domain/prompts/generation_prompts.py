"""Document generation prompts for creating tailored resumes and cover letters."""

from typing import Dict, Any


class GenerationPrompts:
    """Prompts for generating tailored resumes and cover letters using user preferences."""
    
    RESUME_SYSTEM_PROMPT = """You are an expert resume writer and career consultant specializing in ATS-optimized, tailored resume generation. Your task is to create professional resumes that match user writing styles, structural preferences, and target job requirements.

CRITICAL CONSTRAINTS:
- USE ONLY PROVIDED INFORMATION - Never fabricate experiences, skills, or achievements
- MAINTAIN USER STYLE - Apply the provided writing style preferences consistently
- FOLLOW STRUCTURE PREFERENCES - Use the exact layout and formatting preferences provided
- OPTIMIZE FOR ATS - Ensure keyword integration feels natural and appropriate
- PROFESSIONAL QUALITY - Create polished, error-free content

You will be provided with:
1. User's writing style preferences (extracted from their cover letter)
2. User's structural preferences (extracted from their example resumes)
3. User's profile content (experiences, skills, education)
4. Target job analysis and requirements
5. Specific generation options and instructions"""

    COVER_LETTER_SYSTEM_PROMPT = """You are an expert cover letter writer specializing in personalized, compelling cover letters that match user writing styles and target specific job opportunities.

CRITICAL CONSTRAINTS:
- USE ONLY PROVIDED INFORMATION - Never fabricate experiences or achievements
- MAINTAIN USER VOICE - Apply the provided writing style preferences exactly
- TARGETED CONTENT - Address specific job requirements and company needs
- PROFESSIONAL TONE - Maintain appropriate level of formality
- CONCISE LENGTH - Keep to standard cover letter length (300-400 words)

You will generate cover letters that sound like the user wrote them while targeting the specific job opportunity."""

    RESUME_GENERATION_PROMPT = """Generate a tailored resume using the following information:

USER WRITING STYLE PREFERENCES:
{writing_style_config}

USER STRUCTURAL PREFERENCES:
{layout_config}

USER PROFILE CONTENT:
{user_profile}

TARGET JOB ANALYSIS:
{job_analysis}

GENERATION OPTIONS:
- Template: {template_style}
- Length: {target_length}
- Focus Areas: {focus_areas}
- Custom Instructions: {custom_instructions}

GENERATE a complete resume that:
1. Uses ONLY the user's actual experiences, skills, and achievements
2. Applies their writing style preferences (vocabulary, tone, sentence structure)
3. Follows their structural preferences (section order, formatting, bullet styles)
4. Incorporates relevant keywords from the job analysis naturally
5. Optimizes for ATS while maintaining readability
6. Matches the specified template style and length

OUTPUT FORMAT: Markdown with clear sections, professional formatting, and consistent style throughout.

IMPORTANT:
- Do not add experiences or skills not present in the user profile
- Maintain the user's authentic voice and writing patterns
- Ensure all content is truthful and based on provided information
- Integrate job keywords naturally without overuse"""

    COVER_LETTER_GENERATION_PROMPT = """Generate a tailored cover letter using the following information:

USER WRITING STYLE PREFERENCES:
{writing_style_config}

USER PROFILE CONTENT:
{user_profile}

TARGET JOB INFORMATION:
- Job Title: {job_title}
- Company: {company_name}
- Job Analysis: {job_analysis}

GENERATION OPTIONS:
- Company Research: {company_info}
- Tone Preference: {tone_preference}
- Length Preference: {length_preference}
- Custom Instructions: {custom_instructions}

GENERATE a professional cover letter that:
1. Uses ONLY the user's actual experiences and achievements
2. Applies their writing style preferences (vocabulary, tone, sentence structure)
3. Addresses specific job requirements and company needs
4. Demonstrates genuine interest and research
5. Maintains appropriate length (300-400 words)
6. Follows standard cover letter structure

OUTPUT FORMAT: Professional cover letter with proper business format.

IMPORTANT:
- Use the user's authentic voice and writing patterns
- Connect user's experiences to job requirements specifically
- Do not fabricate experiences or exaggerate achievements
- Maintain professional tone while showing personality"""

    CONTENT_OPTIMIZATION_PROMPT = """Optimize the generated content for better ATS performance and readability:

ORIGINAL CONTENT:
{original_content}

JOB KEYWORDS:
{target_keywords}

USER PREFERENCES:
{user_preferences}

OPTIMIZATION GOALS:
- Improve ATS keyword matching without overuse
- Enhance readability and flow
- Maintain user's writing style
- Ensure professional polish

Return optimized content with:
{{
  "optimized_content": "improved version",
  "changes_made": ["change1", "change2"],
  "keyword_integration": {{
    "added": ["keyword1", "keyword2"],
    "frequency": {{"keyword": count}}
  }},
  "style_preservation": "how user style was maintained"
}}"""

    @classmethod
    def get_resume_generation_messages(
        cls,
        writing_style_config: str,
        layout_config: str,
        user_profile: str,
        job_analysis: str,
        template_style: str,
        target_length: str,
        focus_areas: list,
        custom_instructions: str
    ) -> list:
        """Get messages for resume generation."""
        return [
            {"role": "system", "content": cls.RESUME_SYSTEM_PROMPT},
            {"role": "user", "content": cls.RESUME_GENERATION_PROMPT.format(
                writing_style_config=writing_style_config,
                layout_config=layout_config,
                user_profile=user_profile,
                job_analysis=job_analysis,
                template_style=template_style,
                target_length=target_length,
                focus_areas=", ".join(focus_areas) if focus_areas else "None specified",
                custom_instructions=custom_instructions or "None provided"
            )}
        ]
    
    @classmethod
    def get_cover_letter_generation_messages(
        cls,
        writing_style_config: str,
        user_profile: str,
        job_title: str,
        company_name: str,
        job_analysis: str,
        company_info: str,
        tone_preference: str,
        length_preference: str,
        custom_instructions: str
    ) -> list:
        """Get messages for cover letter generation."""
        return [
            {"role": "system", "content": cls.COVER_LETTER_SYSTEM_PROMPT},
            {"role": "user", "content": cls.COVER_LETTER_GENERATION_PROMPT.format(
                writing_style_config=writing_style_config,
                user_profile=user_profile,
                job_title=job_title,
                company_name=company_name,
                job_analysis=job_analysis,
                company_info=company_info or "No additional company information provided",
                tone_preference=tone_preference or "Professional",
                length_preference=length_preference or "Standard (300-400 words)",
                custom_instructions=custom_instructions or "None provided"
            )}
        ]
    
    @classmethod
    def get_optimization_messages(
        cls,
        original_content: str,
        target_keywords: list,
        user_preferences: str
    ) -> list:
        """Get messages for content optimization."""
        return [
            {"role": "system", "content": cls.RESUME_SYSTEM_PROMPT},
            {"role": "user", "content": cls.CONTENT_OPTIMIZATION_PROMPT.format(
                original_content=original_content,
                target_keywords=", ".join(target_keywords),
                user_preferences=user_preferences
            )}
        ]

    @classmethod
    def get_resume_model_config(cls) -> Dict[str, Any]:
        """Get recommended model configuration for resume generation."""
        return {
            "model": "llama-3.3-70b-versatile",  # High-quality model for content generation
            "max_tokens": 3000,
            "temperature": 0.4,  # Balanced creativity and consistency
        }
    
    @classmethod
    def get_cover_letter_model_config(cls) -> Dict[str, Any]:
        """Get recommended model configuration for cover letter generation."""
        return {
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 1500,
            "temperature": 0.5,  # Slightly higher creativity for cover letters
        }