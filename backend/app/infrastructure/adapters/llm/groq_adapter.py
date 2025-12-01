"""Groq LLM adapter implementation."""

import json
import time
from typing import Dict, Optional
from groq import AsyncGroq

from .llm_interface import LLMInterface


class GroqAdapter(LLMInterface):
    """Groq LLM adapter using real API."""
    
    def __init__(self, api_key: str):
        """Initialize Groq client."""
        self.client = AsyncGroq(api_key=api_key)
        self.fast_model = "llama-3.1-8b-instant"  # For ranking, style extraction
        self.quality_model = "llama-3.3-70b-versatile"  # For generation, enhancement
    
    async def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """Generate completion from Groq."""
        start_time = time.time()
        
        if model is None:
            model = self.quality_model
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            processing_time = time.time() - start_time
            
            return {
                "content": response.choices[0].message.content,
                "tokens": response.usage.total_tokens,
                "model": model,
                "processing_time": processing_time,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens
            }
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    async def extract_writing_style(self, sample_text: str) -> Dict:
        """Extract writing style from sample text."""
        prompt = f"""Analyze the writing style of this text and return ONLY a JSON object with these keys:
- tone (string): professional/casual/enthusiastic/formal
- vocabulary_level (string): basic/intermediate/advanced/expert
- sentence_structure (string): simple/complex/varied
- key_phrases (array): 3-5 distinctive phrases or patterns

Text to analyze:
{sample_text[:2000]}

Return ONLY valid JSON, no other text."""

        result = await self.generate_completion(
            prompt=prompt,
            max_tokens=500,
            temperature=0.3,
            model=self.fast_model
        )
        
        try:
            # Extract JSON from response
            content = result["content"].strip()
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            style = json.loads(content.strip())
            return {
                "extracted_style": style,
                "llm_metadata": {
                    "model": result["model"],
                    "tokens": result["tokens"],
                    "processing_time": result["processing_time"]
                }
            }
        except json.JSONDecodeError:
            # Fallback to basic style
            return {
                "extracted_style": {
                    "tone": "professional",
                    "vocabulary_level": "advanced",
                    "sentence_structure": "varied",
                    "key_phrases": []
                },
                "llm_metadata": {
                    "model": result["model"],
                    "tokens": result["tokens"],
                    "processing_time": result["processing_time"],
                    "note": "Used fallback style due to parsing error"
                }
            }
    
    async def enhance_text(self, text: str, style: Optional[Dict] = None) -> str:
        """Enhance text using optional writing style."""
        style_instruction = ""
        if style:
            tone = style.get("tone", "professional")
            vocab = style.get("vocabulary_level", "advanced")
            style_instruction = f"\nMaintain a {tone} tone with {vocab} vocabulary level."
        
        prompt = f"""Enhance this professional text to be more impactful and compelling.{style_instruction}
Use strong action verbs, quantify achievements where possible, and ensure clarity.

Original text:
{text}

STRICT CONTENT RULES:
- Do NOT use emojis or special characters
- Do NOT fabricate, exaggerate, or add information not present in the original text
- ONLY enhance and rephrase what is explicitly stated
- Do NOT add new achievements, skills, or metrics that weren't in the original
- Do NOT invent numbers, dates, or accomplishments
- Maintain complete factual accuracy - only improve clarity and impact of existing content

Return ONLY the enhanced text, no explanations or additional commentary."""

        result = await self.generate_completion(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7,
            model=self.quality_model
        )
        
        return result["content"].strip()
    
    async def enhance_profile_batch(self, profile_data: Dict, style: Optional[Dict] = None) -> Dict:
        """Enhance all profile content in a single LLM request."""
        style_instruction = ""
        if style:
            tone = style.get("tone", "professional")
            vocab = style.get("vocabulary_level", "advanced")
            style_instruction = f"\nMaintain a {tone} tone with {vocab} vocabulary level."
        
        # Build the batch request
        sections_to_enhance = []
        
        # Professional summary
        if profile_data.get("professional_summary"):
            sections_to_enhance.append({
                "type": "summary",
                "id": "summary",
                "text": profile_data["professional_summary"]
            })
        
        # All experiences
        for exp in profile_data.get("experiences", []):
            if exp.get("description"):
                sections_to_enhance.append({
                    "type": "experience",
                    "id": exp["id"],
                    "title": exp.get("title", ""),
                    "company": exp.get("company", ""),
                    "text": exp["description"]
                })
        
        # All projects
        for proj in profile_data.get("projects", []):
            if proj.get("description"):
                sections_to_enhance.append({
                    "type": "project",
                    "id": proj["id"],
                    "name": proj.get("name", ""),
                    "text": proj["description"]
                })
        
        # Format sections for prompt
        sections_text = ""
        for i, section in enumerate(sections_to_enhance, 1):
            if section["type"] == "summary":
                sections_text += f"\n[SECTION_{i}]\nType: Professional Summary\nOriginal: {section['text']}\n"
            elif section["type"] == "experience":
                sections_text += f"\n[SECTION_{i}]\nType: Experience - {section['title']} at {section['company']}\nOriginal: {section['text']}\n"
            else:
                sections_text += f"\n[SECTION_{i}]\nType: Project - {section['name']}\nOriginal: {section['text']}\n"
        
        prompt = f"""Enhance ALL the following professional profile sections to be more impactful and compelling.{style_instruction}
Use strong action verbs, quantify achievements where possible, and ensure clarity.

{sections_text}

STRICT CONTENT RULES:
- Do NOT use emojis or special characters
- Do NOT fabricate, exaggerate, or add information not present in the original text
- ONLY enhance and rephrase what is explicitly stated
- Do NOT add new achievements, skills, or metrics that weren't in the original
- Do NOT invent numbers, dates, or accomplishments
- Maintain complete factual accuracy - only improve clarity and impact of existing content

Return ONLY a JSON object with this structure:
{{
  "sections": [
    {{"section_number": 1, "enhanced_text": "..."}},
    {{"section_number": 2, "enhanced_text": "..."}},
    ...
  ]
}}

Return ONLY valid JSON, no other text."""

        result = await self.generate_completion(
            prompt=prompt,
            max_tokens=4000,  # Larger for batch processing
            temperature=0.3,  # Lower temperature for more consistent JSON formatting
            model=self.quality_model,
            response_format={"type": "json_object"}  # Force JSON output (if supported by model)
        )
        
        try:
            content = result["content"].strip()
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            enhanced_data = json.loads(content)
            
            # Validate structure
            if "sections" not in enhanced_data or not isinstance(enhanced_data["sections"], list):
                raise ValueError("Invalid response structure: missing 'sections' array")
            
            # Map enhanced text back to sections
            enhancements = {}
            sections_found = 0
            
            for i, section in enumerate(sections_to_enhance, 1):
                # Find matching enhanced section
                enhanced_section = next(
                    (s for s in enhanced_data.get("sections", []) if s.get("section_number") == i),
                    None
                )
                if enhanced_section and "enhanced_text" in enhanced_section:
                    enhancements[section["id"]] = {
                        "type": section["type"],
                        "enhanced_text": enhanced_section["enhanced_text"]
                    }
                    sections_found += 1
            
            return {
                "enhancements": enhancements,
                "llm_metadata": {
                    "model": result["model"],
                    "tokens": result["tokens"],
                    "processing_time": result["processing_time"],
                    "sections_enhanced": sections_found,
                    "sections_requested": len(sections_to_enhance),
                    "success_rate": f"{(sections_found/len(sections_to_enhance)*100):.1f}%"
                }
            }
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback: return empty enhancements with detailed error
            return {
                "enhancements": {},
                "llm_metadata": {
                    "model": result["model"],
                    "tokens": result["tokens"],
                    "processing_time": result["processing_time"],
                    "error": f"Parsing failed: {str(e)}",
                    "raw_response_preview": result["content"][:200] if "content" in result else "N/A"
                }
            }
    
    async def rank_content(
        self,
        job_description: str,
        experiences: list,
        projects: list
    ) -> Dict:
        """Rank content by relevance to job.
        
        Note: experiences and projects should have integer 'id' fields (1, 2, 3, etc.)
        for optimal LLM performance. The service layer handles UUID mapping.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Format experiences
        exp_text = "\n\n".join([
            f"ID: {exp['id']}\nTitle: {exp['title']}\nCompany: {exp['company']}\nDescription: {exp.get('description', '')}"
            for exp in experiences
        ])
        
        # Format projects
        proj_text = "\n\n".join([
            f"ID: {proj['id']}\nName: {proj['name']}\nDescription: {proj.get('description', '')}\nTech: {', '.join(proj.get('technologies', []))}"
            for proj in projects
        ])
        
        prompt = f"""Analyze this job description and rank ALL experiences and ALL projects by relevance.

Job Description:
{job_description}

EXPERIENCES:
{exp_text}

PROJECTS:
{proj_text}

CRITICAL RANKING RULES:
1. You MUST include EVERY SINGLE experience ID in ranked_experience_ids
2. You MUST include EVERY SINGLE project ID in ranked_project_ids  
3. DO NOT omit any IDs - include them all, even completely irrelevant ones
4. Rank from MOST relevant (first) to LEAST relevant (last)
5. Non-technical experiences (retail, food service, etc.) go LAST
6. Your ranked_experience_ids array MUST have exactly {len(experiences)} items
7. Your ranked_project_ids array MUST have exactly {len(projects)} items

Example for 4 experiences where 3,4 are relevant and 1,2 are not:
{{"ranked_experience_ids": [3, 4, 1, 2]}}  ← ALL 4 IDs included, relevant first

Return ONLY a JSON object:
{{
  "ranked_experience_ids": [ALL experience IDs from most to least relevant],
  "ranked_project_ids": [ALL project IDs from most to least relevant],
  "keyword_matches": {{"keyword": count, ...}},
  "ranking_rationale": "brief explanation"
}}

Return ONLY valid JSON. No markdown, no extra text."""

        logger.info(f"FULL PROMPT TO LLM:\n{prompt[:1000]}...")
        
        result = await self.generate_completion(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.3,
            model=self.fast_model
        )
        
        logger.info(f"RAW LLM RESPONSE: {result['content'][:500]}...")
        
        try:
            content = result["content"].strip()
            
            # Remove markdown code blocks
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            # Remove JSON comments (// ...) which are not valid JSON
            import re
            content = re.sub(r'//.*?(?=\n|$)', '', content)
            
            # Extract JSON if there's extra text after it
            # Look for the closing brace of the main JSON object
            if content.startswith("{"):
                # Find the matching closing brace
                brace_count = 0
                json_end = -1
                for i, char in enumerate(content):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                
                if json_end > 0:
                    content = content[:json_end]
            
            logger.info(f"CLEANED JSON for parsing: {content[:300]}...")
            ranking = json.loads(content.strip())
            
            logger.info(f"✓ Successfully parsed ranking JSON")
            
            return {
                "ranked_experience_ids": ranking.get("ranked_experience_ids", [exp["id"] for exp in experiences]),
                "ranked_project_ids": ranking.get("ranked_project_ids", [proj["id"] for proj in projects]),
                "keyword_matches": ranking.get("keyword_matches", {}),
                "ranking_rationale": ranking.get("ranking_rationale", "Ranked by relevance to job requirements"),
                "llm_metadata": {
                    "model": result["model"],
                    "tokens": result["tokens"],
                    "processing_time": result["processing_time"]
                }
            }
        except json.JSONDecodeError as e:
            # Fallback: return original order
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Failed content: {content[:500] if 'content' in locals() else 'N/A'}")
            return {
                "ranked_experience_ids": [exp["id"] for exp in experiences],
                "ranked_project_ids": [proj["id"] for proj in projects],
                "keyword_matches": {},
                "ranking_rationale": "Original order (parsing error)",
                "llm_metadata": {
                    "model": result["model"],
                    "tokens": result["tokens"],
                    "processing_time": result["processing_time"],
                    "note": "Used fallback ranking"
                }
            }
    
    async def generate_cover_letter(
        self,
        job_description: str,
        profile_data: Dict,
        writing_style: Optional[Dict] = None,
        company_name: Optional[str] = None,
        hiring_manager: Optional[str] = None,
        max_paragraphs: int = 4
    ) -> str:
        """Generate personalized cover letter."""
        style_instruction = ""
        if writing_style:
            tone = writing_style.get("tone", "professional")
            vocab = writing_style.get("vocabulary_level", "advanced")
            style_instruction = f"\nWriting style: {tone} tone, {vocab} vocabulary level."
        
        # Extract key info from profile
        name = profile_data.get("full_name", "")
        summary = profile_data.get("professional_summary", "")
        experiences = profile_data.get("experiences", [])  # ALL experiences
        projects = profile_data.get("projects", [])  # ALL projects
        skills = profile_data.get("skills", {})
        education = profile_data.get("education", [])
        
        # Format ALL experiences with full context
        exp_text = "\n".join([
            f"- {exp.get('title')} at {exp.get('company')} ({exp.get('start_date', '')} - {exp.get('end_date', 'Present')})\n  {exp.get('description', '')}\n  Achievements: {', '.join(exp.get('achievements', []))}"
            for exp in experiences
        ])
        
        # Format ALL projects with full details
        proj_text = "\n".join([
            f"- {proj.get('name')}: {proj.get('description', '')}\n  Technologies: {', '.join(proj.get('technologies', []))}"
            for proj in projects
        ])
        
        # Format skills
        tech_skills = ", ".join(skills.get("technical", []))
        soft_skills = ", ".join(skills.get("soft", []))
        
        # Format education
        edu_text = "\n".join([
            f"- {edu.get('degree')} in {edu.get('field_of_study')} from {edu.get('institution')} (GPA: {edu.get('gpa', 'N/A')})"
            for edu in education
        ])
        
        greeting = f"Dear {hiring_manager}," if hiring_manager else "Dear Hiring Manager,"
        company_ref = company_name if company_name else "[Company Name]"
        
        prompt = f"""Write a compelling, personalized cover letter for this job application.{style_instruction}

Job Description:
{job_description}

Candidate Profile:
Name: {name}

Professional Summary:
{summary}

Complete Work Experience:
{exp_text}

All Projects:
{proj_text}

Technical Skills: {tech_skills}
Soft Skills: {soft_skills}

Education:
{edu_text}

Requirements:
- {max_paragraphs} paragraphs maximum
- Start with: {greeting}
- Reference company: {company_ref}
- Draw from ALL experiences and projects to find the most relevant examples
- Highlight specific achievements with quantifiable results when possible
- Demonstrate deep understanding of the role by connecting candidate's full background to job requirements
- Show genuine enthusiasm and cultural fit
- Professional yet personable tone
- Use the candidate's complete work history to craft compelling narratives

CRITICAL - Keyword Optimization:
- CAREFULLY analyze the job description for key technical skills, tools, frameworks, and industry buzzwords
- STRATEGICALLY weave these exact keywords naturally throughout the cover letter
- Match terminology from job description (e.g., if job says "React.js", use "React.js" not just "React")
- Prioritize experiences and projects that contain technologies/skills mentioned in the job description
- Include specific technical terms and certifications that align with job requirements
- Mirror the language and phrasing used in the job posting to maximize ATS compatibility
- Ensure keywords flow naturally - avoid keyword stuffing
- Focus on demonstrating actual experience with the required technologies by citing specific projects/roles

STRICT CONTENT RULES:
- Do NOT use emojis or special characters
- Do NOT fabricate, exaggerate, or invent any experiences, skills, achievements, or qualifications
- ONLY use information explicitly provided in the candidate's profile
- Do NOT add technologies, tools, or skills not listed in the candidate's experience
- Do NOT claim proficiency in areas not demonstrated in the provided work history
- Do NOT invent metrics, dates, or accomplishments
- If the candidate lacks certain job requirements, focus on transferable skills instead of making up experience
- Maintain complete honesty and authenticity - hiring managers will verify claims

Return ONLY the cover letter text, no additional commentary."""

        result = await self.generate_completion(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.8,
            model=self.quality_model
        )
        
        return result["content"].strip()
    
    async def calculate_ats_score(
        self,
        document_text: str,
        job_description: str,
        job_keywords: list
    ) -> Dict:
        """Calculate ATS compatibility score using LLM analysis."""
        keywords_str = ", ".join(job_keywords[:50])  # Limit to first 50 keywords
        
        prompt = f"""Analyze this resume/cover letter for ATS (Applicant Tracking System) compatibility with the job description.

Job Description:
{job_description[:1500]}

Key Required Skills/Keywords:
{keywords_str}

Document to Analyze:
{document_text[:3000]}

Analyze the document and return ONLY a JSON object with this structure:
{{
  "score": <number 0-100>,
  "matched_keywords": ["keyword1", "keyword2", ...],
  "missing_keywords": ["keyword1", "keyword2", ...],
  "suggestions": ["suggestion1", "suggestion2", ...],
  "analysis": "brief explanation of the score"
}}

Scoring Guidelines:
- 90-100: Excellent match with most/all required skills and keywords
- 80-89: Strong match with majority of requirements
- 70-79: Good match with solid keyword coverage
- 60-69: Moderate match, missing some key requirements
- 50-59: Weak match, significant gaps in requirements
- Below 50: Poor match, major misalignment

Return ONLY valid JSON."""

        result = await self.generate_completion(
            prompt=prompt,
            max_tokens=800,
            temperature=0.3,
            model=self.fast_model
        )
        
        try:
            content = result["content"].strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            ats_data = json.loads(content.strip())
            
            return {
                "score": float(ats_data.get("score", 75.0)),
                "matched_keywords": ats_data.get("matched_keywords", []),
                "missing_keywords": ats_data.get("missing_keywords", []),
                "suggestions": ats_data.get("suggestions", []),
                "analysis": ats_data.get("analysis", ""),
                "llm_metadata": {
                    "model": result["model"],
                    "tokens": result["tokens"],
                    "processing_time": result["processing_time"]
                }
            }
        except (json.JSONDecodeError, ValueError, KeyError):
            # Fallback to simple keyword matching
            text_lower = document_text.lower()
            matched = [kw for kw in job_keywords if kw.lower() in text_lower]
            total = len(job_keywords)
            score = (len(matched) / total * 100) if total > 0 else 75.0
            score = min(max(score, 50.0), 95.0)
            
            return {
                "score": score,
                "matched_keywords": matched[:10],
                "missing_keywords": [kw for kw in job_keywords if kw.lower() not in text_lower][:10],
                "suggestions": ["Add more relevant keywords from job description"],
                "analysis": "Fallback keyword matching used",
                "llm_metadata": {
                    "model": result["model"],
                    "tokens": result["tokens"],
                    "processing_time": result["processing_time"],
                    "note": "Used fallback scoring due to parsing error"
                }
            }
