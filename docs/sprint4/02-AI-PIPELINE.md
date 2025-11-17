# AI Pipeline Architecture - JobWise v3.0

**Version**: 3.0  
**Last Updated**: November 16, 2025  
**Status**: 🎯 **Ready for Implementation**

---

## Pipeline Overview

This document defines the 4 AI-powered workflows in the JobWise system:

1. **Writing Style Extraction** - Analyze sample cover letter to extract style preferences (in-memory, not stored)
2. **Profile Enhancement** - Polish user's profile/experience/project descriptions using extracted style
3. **Job-Specific Content Ranking** - Rank experiences/projects by relevance to specific job
4. **Cover Letter Generation** - Generate tailored cover letter for specific job

**Note**: Resume compilation is NOT in this document (it's pure logic, no LLM).

---

## Workflow 1: Writing Style Extraction

### Purpose
Extract writing style characteristics from user's sample cover letter to apply to profile enhancements.

### Trigger
Called internally by Profile Enhancement workflow (not exposed as API endpoint).

### Input
- Sample cover letter text (from `sample_documents` table)

### Output
- In-memory `WritingStyle` object (NOT stored in database)

### Process Flow

```
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Fetch Sample Cover Letter                           │
├──────────────────────────────────────────────────────────────┤
│ Query: SELECT original_text FROM sample_documents           │
│        WHERE user_id = ? AND document_type = 'cover_letter' │
│        AND is_active = TRUE                                  │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 2: Build Prompt (from prompt_templates table)          │
├──────────────────────────────────────────────────────────────┤
│ Template: "writing_style_extraction"                        │
│ Variables:                                                   │
│   - cover_letter_text: {{ original_text }}                  │
│                                                              │
│ System Message:                                              │
│   "You are an expert writing analyst. Analyze the provided  │
│    cover letter and extract the writer's style."            │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 3: LLM Analysis                                         │
├──────────────────────────────────────────────────────────────┤
│ Model: llama-3.1-8b-instant (fast, analytical)              │
│ Temperature: 0.2 (deterministic)                             │
│ Max Tokens: 1500                                             │
│                                                              │
│ Expected Output Format: JSON                                 │
│ {                                                            │
│   "tone": "semi-formal",                                     │
│   "vocabulary_level": "professional",                        │
│   "sentence_structure": "varied",                            │
│   "active_voice_ratio": 0.85,                                │
│   "action_verbs": ["architected", "implemented", ...],       │
│   "technical_terms": ["AI orchestration", "VR", ...],        │
│   "connector_phrases": ["Throughout my", "This experience"], │
│   "storytelling_style": "achievement-focused"                │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 4: Parse & Validate Response                           │
├──────────────────────────────────────────────────────────────┤
│ Extract JSON from LLM response                               │
│ Validate required fields                                     │
│ Create WritingStyle object (Python dataclass)                │
│                                                              │
│ Fallback: If parsing fails, use default style preferences   │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 5: Return WritingStyle Object (In-Memory)              │
├──────────────────────────────────────────────────────────────┤
│ NOT stored in database                                       │
│ Used immediately for profile enhancement                     │
│ Regenerated on each enhancement request                      │
└──────────────────────────────────────────────────────────────┘
```

### Code Structure

```python
# app/application/services/writing_style_service.py

from dataclasses import dataclass
from typing import List

@dataclass
class WritingStyle:
    """In-memory representation of extracted writing style."""
    tone: str  # formal, semi-formal, enthusiastic, etc.
    vocabulary_level: str  # professional, academic, conversational
    sentence_structure: str  # simple, varied, complex
    active_voice_ratio: float  # 0.0-1.0
    action_verbs: List[str]
    technical_terms: List[str]
    connector_phrases: List[str]
    storytelling_style: str  # achievement-focused, narrative, analytical
    
    def to_prompt_context(self) -> str:
        """Convert to string for embedding in enhancement prompts."""
        return f"""
Writing Style Preferences:
- Tone: {self.tone}
- Vocabulary: {self.vocabulary_level}
- Sentence Structure: {self.sentence_structure}
- Active Voice: {int(self.active_voice_ratio * 100)}%
- Preferred Action Verbs: {', '.join(self.action_verbs[:10])}
- Technical Terms: {', '.join(self.technical_terms[:10])}
- Storytelling Approach: {self.storytelling_style}
"""

class WritingStyleExtractionService:
    """Extract writing style from cover letter."""
    
    async def extract_style(
        self,
        user_id: int,
        sample_documents_repo: SampleDocumentsRepository,
        prompt_templates_repo: PromptTemplatesRepository,
        llm_adapter: ILLMService
    ) -> WritingStyle:
        """
        Extract writing style from active cover letter.
        
        Returns:
            WritingStyle object (in-memory only)
        """
        # Step 1: Fetch sample cover letter
        cover_letter = await sample_documents_repo.get_active_by_type(
            user_id=user_id,
            document_type="cover_letter"
        )
        
        if not cover_letter:
            raise ValueError("No active cover letter found for user")
        
        # Step 2: Build prompt
        template = await prompt_templates_repo.get_default_by_name(
            template_name="writing_style_extraction"
        )
        
        prompt = template.render(
            cover_letter_text=cover_letter.original_text
        )
        
        # Step 3: LLM analysis
        response = await llm_adapter.generate(
            prompt=prompt,
            system_message=template.system_message,
            temperature=template.default_temperature,
            max_tokens=template.default_max_tokens,
            model=template.target_llm_model
        )
        
        # Step 4: Parse response
        style_data = self._parse_llm_response(response)
        
        # Step 5: Create WritingStyle object
        return WritingStyle(
            tone=style_data.get("tone", "semi-formal"),
            vocabulary_level=style_data.get("vocabulary_level", "professional"),
            sentence_structure=style_data.get("sentence_structure", "varied"),
            active_voice_ratio=style_data.get("active_voice_ratio", 0.7),
            action_verbs=style_data.get("action_verbs", []),
            technical_terms=style_data.get("technical_terms", []),
            connector_phrases=style_data.get("connector_phrases", []),
            storytelling_style=style_data.get("storytelling_style", "achievement-focused")
        )
    
    def _parse_llm_response(self, response: str) -> dict:
        """Parse JSON from LLM response with fallback."""
        try:
            # Extract JSON from response
            import json
            import re
            
            # Find JSON block
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            # Fallback to default
            return {}
        except Exception as e:
            logger.warning(f"Failed to parse writing style response: {e}")
            return {}
```

### Prompt Template Example

```json
{
  "id": "template-writing-style-v1",
  "template_name": "writing_style_extraction",
  "template_version": "1.0.0",
  "description": "Extract writing style characteristics from cover letter",
  "prompt_template": "Analyze the following cover letter and extract the writer's style characteristics:\n\n{{ cover_letter_text }}\n\nProvide your analysis in JSON format with these fields:\n- tone (formal/semi-formal/enthusiastic/authoritative/collaborative)\n- vocabulary_level (professional/academic/conversational/technical)\n- sentence_structure (simple/compound/complex/varied)\n- active_voice_ratio (0.0-1.0 decimal)\n- action_verbs (list of 10-15 strong verbs used)\n- technical_terms (list of 10-15 domain-specific terms)\n- connector_phrases (list of 5-10 transition phrases)\n- storytelling_style (narrative/achievement-focused/analytical/problem-solution)\n\nBe precise and extract actual examples from the text.",
  "system_message": "You are an expert writing analyst with deep knowledge of professional communication styles. Your task is to identify patterns in writing that can be replicated.",
  "expected_output_format": "JSON",
  "default_temperature": 0.2,
  "default_max_tokens": 1500,
  "target_llm_model": "llama-3.1-8b-instant"
}
```

---

## Workflow 2: Profile Enhancement

### Purpose
Enhance user's profile summary, experience descriptions, and project descriptions using their writing style.

### Trigger
User clicks "Enhance Profile" button → POST `/profile/enhance`

### Input
- User ID
- Profile ID
- Writing style (extracted from sample cover letter)

### Output
- Enhanced text stored in database columns:
  - `master_profiles.enhanced_professional_summary`
  - `experiences.enhanced_description`
  - `projects.enhanced_description`

### Process Flow

```
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Extract Writing Style                               │
├──────────────────────────────────────────────────────────────┤
│ Call WritingStyleExtractionService.extract_style()          │
│ Returns: WritingStyle object (in-memory)                     │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 2: Fetch Profile Data                                  │
├──────────────────────────────────────────────────────────────┤
│ Query profile, experiences, projects from database           │
│ Include original text fields only                            │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 3: Enhance Professional Summary                        │
├──────────────────────────────────────────────────────────────┤
│ Template: "profile_summary_enhancement"                     │
│ Variables:                                                   │
│   - original_summary: {{ professional_summary }}             │
│   - writing_style: {{ writing_style.to_prompt_context() }}  │
│                                                              │
│ LLM Model: llama-3.3-70b-versatile (high quality)           │
│ Temperature: 0.3                                             │
│                                                              │
│ Output: Enhanced summary text                                │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 4: Enhance Each Experience Description                 │
├──────────────────────────────────────────────────────────────┤
│ For each experience:                                         │
│   Template: "experience_enhancement"                         │
│   Variables:                                                 │
│     - title: {{ experience.title }}                          │
│     - company: {{ experience.company }}                      │
│     - original_description: {{ experience.description }}     │
│     - achievements: {{ experience.achievements }}            │
│     - writing_style: {{ writing_style.to_prompt_context() }}│
│                                                              │
│   LLM Model: llama-3.3-70b-versatile                         │
│   Output: Enhanced description                               │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 5: Enhance Each Project Description                    │
├──────────────────────────────────────────────────────────────┤
│ Similar to Step 4 but for projects                          │
│ Template: "project_enhancement"                              │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 6: Store Enhanced Text in Database                     │
├──────────────────────────────────────────────────────────────┤
│ UPDATE master_profiles SET                                   │
│   enhanced_professional_summary = ?,                         │
│   enhancement_metadata = ?                                   │
│ WHERE id = ?                                                 │
│                                                              │
│ UPDATE experiences SET                                       │
│   enhanced_description = ?,                                  │
│   enhancement_metadata = ?                                   │
│ WHERE id = ?                                                 │
│                                                              │
│ UPDATE projects SET                                          │
│   enhanced_description = ?,                                  │
│   enhancement_metadata = ?                                   │
│ WHERE id = ?                                                 │
└──────────────────────────────────────────────────────────────┘
```

### Code Structure

```python
# app/application/services/profile_enhancement_service.py

class ProfileEnhancementService:
    """Enhance user profile using extracted writing style."""
    
    async def enhance_profile(
        self,
        user_id: int,
        profile_id: str,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enhance all profile content using writing style from cover letter.
        
        Args:
            user_id: User ID
            profile_id: Profile UUID
            custom_prompt: Optional user custom instructions
            
        Returns:
            Enhancement results with metadata
        """
        # Step 1: Extract writing style
        writing_style = await self.writing_style_service.extract_style(user_id)
        
        # Step 2: Fetch profile data
        profile = await self.profile_repo.get_by_id(profile_id)
        experiences = await self.experience_repo.get_by_profile_id(profile_id)
        projects = await self.project_repo.get_by_profile_id(profile_id)
        
        # Step 3: Enhance professional summary
        enhanced_summary = await self._enhance_summary(
            original=profile.professional_summary,
            writing_style=writing_style,
            custom_prompt=custom_prompt
        )
        
        # Step 4: Enhance experiences
        enhanced_experiences = []
        for exp in experiences:
            enhanced_desc = await self._enhance_experience(
                experience=exp,
                writing_style=writing_style,
                custom_prompt=custom_prompt
            )
            enhanced_experiences.append({
                "id": exp.id,
                "enhanced_description": enhanced_desc
            })
        
        # Step 5: Enhance projects
        enhanced_projects = []
        for proj in projects:
            enhanced_desc = await self._enhance_project(
                project=proj,
                writing_style=writing_style,
                custom_prompt=custom_prompt
            )
            enhanced_projects.append({
                "id": proj.id,
                "enhanced_description": enhanced_desc
            })
        
        # Step 6: Store in database
        metadata = {
            "llm_model": "llama-3.3-70b-versatile",
            "enhanced_at": datetime.utcnow().isoformat(),
            "writing_style_source": "sample_cover_letter",
            "total_tokens_used": self.total_tokens_used,
            "custom_prompt_used": custom_prompt is not None
        }
        
        await self.profile_repo.update_enhanced_summary(
            profile_id=profile_id,
            enhanced_summary=enhanced_summary,
            metadata=metadata
        )
        
        for enh_exp in enhanced_experiences:
            await self.experience_repo.update_enhanced_description(
                experience_id=enh_exp["id"],
                enhanced_description=enh_exp["enhanced_description"],
                metadata=metadata
            )
        
        for enh_proj in enhanced_projects:
            await self.project_repo.update_enhanced_description(
                project_id=enh_proj["id"],
                enhanced_description=enh_proj["enhanced_description"],
                metadata=metadata
            )
        
        return {
            "success": True,
            "profile_id": profile_id,
            "enhanced_summary": enhanced_summary,
            "enhanced_experiences_count": len(enhanced_experiences),
            "enhanced_projects_count": len(enhanced_projects),
            "total_tokens_used": self.total_tokens_used,
            "total_time_seconds": self.total_time
        }
    
    async def _enhance_summary(
        self,
        original: str,
        writing_style: WritingStyle,
        custom_prompt: Optional[str]
    ) -> str:
        """Enhance professional summary."""
        template = await self.prompt_repo.get_default_by_name("profile_summary_enhancement")
        
        prompt = template.render(
            original_summary=original,
            writing_style=writing_style.to_prompt_context(),
            user_custom_prompt=custom_prompt or ""
        )
        
        response = await self.llm_adapter.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=500,
            model="llama-3.3-70b-versatile"
        )
        
        return self._extract_text(response)
```

### Anti-Fabrication Rules

**CRITICAL**: Enhancement must NOT fabricate content. The prompts include strict rules:

```
RULES FOR ENHANCEMENT:
1. ONLY use information provided in the original text
2. DO NOT invent new experiences, skills, or achievements
3. DO NOT add specific numbers or dates not in the original
4. DO NOT change the factual meaning of any statement
5. ONLY improve clarity, flow, and stylistic consistency
6. If the original is vague, stay vague (do not add specifics)

Your task is to REWRITE, not to CREATE new content.
```

### Prompt Template Example

```json
{
  "id": "template-profile-summary-v1",
  "template_name": "profile_summary_enhancement",
  "template_version": "1.0.0",
  "prompt_template": "Enhance the following professional summary to match the provided writing style.\n\nORIGINAL SUMMARY:\n{{ original_summary }}\n\n{{ writing_style }}\n\n{% if user_custom_prompt %}\nADDITIONAL INSTRUCTIONS:\n{{ user_custom_prompt }}\n{% endif %}\n\nRULES:\n1. ONLY use information from the original summary\n2. DO NOT fabricate experiences or skills\n3. DO NOT add specific numbers not in the original\n4. Improve clarity and style consistency\n5. Match the tone and vocabulary level specified\n\nProvide ONLY the enhanced summary text, no explanations.",
  "system_message": "You are a professional resume writer specializing in enhancing career summaries while maintaining factual accuracy.",
  "default_temperature": 0.3,
  "default_max_tokens": 500,
  "target_llm_model": "llama-3.3-70b-versatile"
}
```

---

## Workflow 3: Job-Specific Content Ranking

### Purpose
Rank user's experiences and projects by relevance to a specific job posting.

### Trigger
User selects job → POST `/rankings/create`

### Input
- User ID
- Job ID
- Optional custom prompt

### Output
- Ranked lists stored in `job_content_rankings` table
- Rankings used for resume compilation

### Process Flow

```
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Fetch Job Description                               │
├──────────────────────────────────────────────────────────────┤
│ Query: SELECT title, description, requirements              │
│        FROM jobs WHERE id = ?                                │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 2: Fetch User's Enhanced Content                       │
├──────────────────────────────────────────────────────────────┤
│ Query experiences with enhanced_description                  │
│ Query projects with enhanced_description                     │
│ Fallback to original description if enhanced is NULL        │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 3: Build Ranking Prompt                                │
├──────────────────────────────────────────────────────────────┤
│ Template: "content_ranking"                                  │
│ Variables:                                                   │
│   - job_title: {{ job.title }}                               │
│   - job_description: {{ job.description }}                   │
│   - job_requirements: {{ job.requirements }}                 │
│   - experiences: {{ experiences_json }}                      │
│   - projects: {{ projects_json }}                            │
│   - user_custom_prompt: {{ custom_prompt }}                  │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 4: LLM Ranking                                          │
├──────────────────────────────────────────────────────────────┤
│ Model: llama-3.1-8b-instant (fast, analytical)              │
│ Temperature: 0.2 (deterministic)                             │
│ Max Tokens: 2000                                             │
│                                                              │
│ Expected Output: JSON                                        │
│ {                                                            │
│   "ranked_experience_ids": ["exp-3", "exp-1", "exp-2"],     │
│   "ranked_project_ids": ["proj-5", "proj-1"],               │
│   "rationale": "Prioritized VR research...",                 │
│   "keyword_matches": {"Python": 3, "AI": 2},                 │
│   "relevance_scores": {                                      │
│     "exp-3": 0.95,                                           │
│     "proj-5": 0.91                                           │
│   }                                                          │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 5: Store Ranking in Database                           │
├──────────────────────────────────────────────────────────────┤
│ INSERT INTO job_content_rankings ... ON CONFLICT UPDATE     │
│ Metadata: tokens used, generation time, prompt template     │
└──────────────────────────────────────────────────────────────┘
```

### Ranking Algorithm (LLM-Powered)

The LLM considers:
1. **Keyword Matching**: How many job requirements appear in content?
2. **Skill Relevance**: Do technical skills align with job?
3. **Seniority Level**: Does experience match job level?
4. **Recency**: More recent experiences ranked higher (if equal relevance)
5. **Impact**: Experiences with quantified achievements ranked higher

### Prompt Template Example

```json
{
  "id": "template-content-ranking-v1",
  "template_name": "content_ranking",
  "template_version": "1.0.0",
  "prompt_template": "You are an expert resume optimizer. Rank the following experiences and projects by relevance to the job posting.\n\nJOB POSTING:\nTitle: {{ job_title }}\nDescription: {{ job_description }}\nRequirements: {{ job_requirements }}\n\nUSER'S EXPERIENCES:\n{{ experiences }}\n\nUSER'S PROJECTS:\n{{ projects }}\n\n{% if user_custom_prompt %}\nADDITIONAL INSTRUCTIONS:\n{{ user_custom_prompt }}\n{% endif %}\n\nRank the experiences and projects by relevance to this job. Provide:\n1. ranked_experience_ids: Array of experience IDs in priority order (highest first)\n2. ranked_project_ids: Array of project IDs in priority order\n3. rationale: Brief explanation of ranking strategy\n4. keyword_matches: Object mapping keywords to count\n5. relevance_scores: Object mapping content IDs to scores (0.0-1.0)\n\nOutput ONLY JSON, no explanations.",
  "system_message": "You are an ATS optimization expert who understands how to match candidate experience to job requirements.",
  "default_temperature": 0.2,
  "default_max_tokens": 2000,
  "target_llm_model": "llama-3.1-8b-instant"
}
```

---

## Workflow 4: Cover Letter Generation

### Purpose
Generate a tailored cover letter for a specific job using user's writing style and profile.

### Trigger
User clicks "Generate Cover Letter" → POST `/generations/cover-letter`

### Input
- User ID
- Profile ID
- Job ID
- Optional custom prompt

### Output
- Generated cover letter stored in `generations` table

### Process Flow

```
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Fetch Sample Cover Letter                           │
├──────────────────────────────────────────────────────────────┤
│ Query active sample cover letter for structure reference     │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 2: Extract Writing Style                               │
├──────────────────────────────────────────────────────────────┤
│ Call WritingStyleExtractionService.extract_style()          │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 3: Fetch Job & Profile Data                            │
├──────────────────────────────────────────────────────────────┤
│ Job: title, company, description, requirements               │
│ Profile: enhanced summary, top 2-3 experiences/projects     │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 4: Build Generation Prompt                             │
├──────────────────────────────────────────────────────────────┤
│ Template: "cover_letter_generation"                         │
│ Variables:                                                   │
│   - sample_cover_letter: {{ sample_text }}                  │
│   - writing_style: {{ writing_style.to_prompt_context() }}  │
│   - job: {{ job_json }}                                      │
│   - profile_summary: {{ enhanced_summary }}                  │
│   - top_experiences: {{ top_experiences_json }}              │
│   - user_custom_prompt: {{ custom_prompt }}                  │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 5: LLM Generation                                       │
├──────────────────────────────────────────────────────────────┤
│ Model: llama-3.3-70b-versatile (high quality writing)       │
│ Temperature: 0.4 (creative but controlled)                   │
│ Max Tokens: 1500                                             │
│                                                              │
│ Output: Complete cover letter text                           │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 6: Store in Generations Table                          │
├──────────────────────────────────────────────────────────────┤
│ INSERT INTO generations (                                    │
│   document_type = 'cover_letter',                           │
│   result = cover_letter_text,                               │
│   user_custom_prompt = custom_prompt,                       │
│   ...                                                        │
│ )                                                            │
└──────────────────────────────────────────────────────────────┘
```

### Anti-Fabrication Rules

```
CRITICAL RULES:
1. Use ONLY experiences and achievements from provided profile
2. DO NOT invent projects, roles, or skills
3. DO NOT add specific numbers or dates not in profile
4. Match the tone and style of the sample cover letter
5. Customize for the specific job and company
6. Keep length similar to sample (±50 words)
```

### Prompt Template Example

```json
{
  "id": "template-cover-letter-v1",
  "template_name": "cover_letter_generation",
  "template_version": "1.0.0",
  "prompt_template": "Generate a tailored cover letter for this job application.\n\nSAMPLE COVER LETTER (for style reference):\n{{ sample_cover_letter }}\n\n{{ writing_style }}\n\nJOB POSTING:\nCompany: {{ job.company }}\nTitle: {{ job.title }}\nDescription: {{ job.description }}\n\nCANDIDATE PROFILE:\nSummary: {{ profile_summary }}\n\nTop Relevant Experiences:\n{{ top_experiences }}\n\n{% if user_custom_prompt %}\nADDITIONAL INSTRUCTIONS:\n{{ user_custom_prompt }}\n{% endif %}\n\nCRITICAL RULES:\n1. Use ONLY information from the candidate profile\n2. Match the writing style and tone of the sample\n3. Customize for this specific job and company\n4. DO NOT fabricate experiences or skills\n5. Length: ~300-500 words\n\nGenerate the cover letter:",
  "system_message": "You are an expert career advisor who writes compelling, authentic cover letters that match the candidate's voice.",
  "default_temperature": 0.4,
  "default_max_tokens": 1500,
  "target_llm_model": "llama-3.3-70b-versatile"
}
```

---

## Performance Targets

| Workflow | LLM Model | Target Time | Max Tokens |
|----------|-----------|-------------|------------|
| Writing Style Extraction | Llama 3.1 8B Instant | <2s | 1500 |
| Profile Summary Enhancement | Llama 3.3 70B Versatile | <3s | 500 |
| Experience Enhancement (each) | Llama 3.3 70B Versatile | <2s | 400 |
| Project Enhancement (each) | Llama 3.3 70B Versatile | <2s | 400 |
| **Total Profile Enhancement** | | **<15s** | ~3000 |
| Content Ranking | Llama 3.1 8B Instant | <3s | 2000 |
| Cover Letter Generation | Llama 3.3 70B Versatile | <5s | 1500 |

---

## Error Handling

### LLM Timeout
- Retry up to 3 times with exponential backoff
- If all retries fail, return error to user with option to retry manually

### Invalid JSON Response
- Attempt to extract JSON from markdown code blocks
- If parsing fails, use default/fallback values
- Log warning for monitoring

### Missing Sample Documents
- Return clear error: "Please upload sample cover letter first"
- Provide link to sample upload page

### Rate Limiting (Groq)
- Respect API rate limits
- Queue requests if necessary
- Show user estimated wait time

---

## Next Steps

1. Review AI pipeline workflows
2. Approve prompt templates
3. Implement services in order: Style → Enhancement → Ranking → Cover Letter
4. Proceed to [03-API-ENDPOINTS.md](03-API-ENDPOINTS.md)
