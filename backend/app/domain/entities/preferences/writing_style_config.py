"""Writing style configuration domain entity."""

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
import uuid


class LanguagePatterns(BaseModel):
    """Language pattern preferences extracted from user writing."""
    action_verbs: List[str] = Field(default_factory=list, max_length=20)
    technical_terms: List[str] = Field(default_factory=list, max_length=30)
    connector_phrases: List[str] = Field(default_factory=list, max_length=15)
    emphasis_words: List[str] = Field(default_factory=list, max_length=15)
    qualification_language: List[str] = Field(default_factory=list, max_length=10)


class ContentApproach(BaseModel):
    """Content approach preferences."""
    storytelling_style: Literal["narrative", "achievement-focused", "analytical", "problem-solution"] = "achievement-focused"
    evidence_style: Literal["quantitative", "qualitative", "mixed", "conceptual"] = "mixed"
    example_integration: Literal["sparse", "moderate", "rich"] = "moderate"
    industry_language_usage: Literal["minimal", "appropriate", "heavy"] = "appropriate"


class WritingStyleConfig(BaseModel):
    """Writing style configuration extracted from user's cover letter."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int
    
    # Core writing characteristics
    vocabulary_level: Literal["professional", "academic", "conversational", "technical"] = "professional"
    vocabulary_complexity_score: int = Field(default=5, ge=1, le=10)
    tone: Literal["formal", "semi-formal", "enthusiastic", "authoritative", "collaborative"] = "semi-formal"
    formality_level: int = Field(default=5, ge=1, le=10)
    
    # Sentence structure preferences
    sentence_structure: Literal["simple", "compound", "complex", "varied"] = "varied"
    avg_sentence_length: Literal["short", "medium", "long"] = "medium"
    active_voice_ratio: float = Field(default=0.7, ge=0.0, le=1.0)
    first_person_frequency: Literal["rare", "moderate", "frequent"] = "moderate"
    
    # Style elements
    transition_style: Literal["minimal", "standard", "elaborate"] = "standard"
    paragraph_length: Literal["short", "medium", "long"] = "medium"
    closing_style: Literal["direct", "warm", "formal", "enthusiastic"] = "warm"
    
    # Language patterns
    language_patterns: LanguagePatterns = Field(default_factory=LanguagePatterns)
    content_approach: ContentApproach = Field(default_factory=ContentApproach)
    
    # Metadata
    source_document_type: Literal["cover_letter", "email", "personal_statement"] = "cover_letter"
    source_document_hash: Optional[str] = None  # For tracking source
    extraction_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_prompt_context(self) -> str:
        """Convert to string format for LLM prompts."""
        return f"""
Writing Style Preferences:
- Vocabulary Level: {self.vocabulary_level} (complexity: {self.vocabulary_complexity_score}/10)
- Tone: {self.tone} (formality: {self.formality_level}/10)
- Sentence Structure: {self.sentence_structure}, {self.avg_sentence_length} length
- Voice: {int(self.active_voice_ratio * 100)}% active voice, {self.first_person_frequency} first-person usage
- Transitions: {self.transition_style}, {self.paragraph_length} paragraphs
- Closing Style: {self.closing_style}

Language Patterns:
- Preferred Action Verbs: {', '.join(self.language_patterns.action_verbs[:10])}
- Technical Terms Usage: {', '.join(self.language_patterns.technical_terms[:8])}
- Connection Phrases: {', '.join(self.language_patterns.connector_phrases[:5])}

Content Approach:
- Storytelling: {self.content_approach.storytelling_style}
- Evidence Style: {self.content_approach.evidence_style}
- Example Integration: {self.content_approach.example_integration}
- Industry Language: {self.content_approach.industry_language_usage}
"""