"""
Writing Style Service - Separate table storage (V3.0).

Extracts writing style characteristics from sample cover letter text
and stores results in dedicated writing_styles table.
"""

import logging
import re
import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from collections import Counter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.infrastructure.database.models import WritingStyleModel, SampleDocumentModel

logger = logging.getLogger(__name__)


class WritingStyleService:
    """
    Service for extracting writing style from sample text.
    
    Stores extracted style in dedicated writing_styles table for normalization and caching.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        self.db = db
    
    # Common action verbs by strength
    STRONG_ACTION_VERBS = {
        "achieved", "spearheaded", "orchestrated", "pioneered", "transformed",
        "revolutionized", "optimized", "architected", "engineered", "delivered"
    }
    
    MODERATE_ACTION_VERBS = {
        "developed", "implemented", "created", "managed", "led",
        "designed", "built", "established", "coordinated", "executed"
    }
    
    WEAK_ACTION_VERBS = {
        "helped", "assisted", "worked", "participated", "contributed",
        "involved", "responsible", "duties", "tasked"
    }
    
    # Connector phrases by formality
    FORMAL_CONNECTORS = {
        "furthermore", "moreover", "consequently", "nevertheless", "notwithstanding",
        "accordingly", "therefore", "subsequently", "additionally", "alternatively"
    }
    
    INFORMAL_CONNECTORS = {
        "and", "but", "so", "because", "when", "while", "or", "also"
    }
    
    TECHNICAL_TERMS = {
        "API", "REST", "GraphQL", "microservices", "kubernetes", "docker", "AWS", "Azure", "GCP",
        "React", "Angular", "Vue", "Node.js", "Python", "Java", "C++", "JavaScript", "TypeScript",
        "SQL", "NoSQL", "MongoDB", "PostgreSQL", "Redis", "Elasticsearch", "Kafka", "Jenkins",
        "CI/CD", "DevOps", "Agile", "Scrum", "machine learning", "AI", "deep learning", "neural networks"
    }
    
    async def get_or_extract_style(self, user_id: int) -> Dict[str, Any]:
        """
        Get cached writing style for user or extract from cover letter sample.
        
        Args:
            user_id: User identifier
            
        Returns:
            Writing style analysis dictionary
            
        Raises:
            ValueError: If no cover letter sample found and no cached style
        """
        logger.info(f"Getting writing style for user {user_id}")
        
        # Check if user already has extracted style
        result = await self.db.execute(
            select(WritingStyleModel).where(WritingStyleModel.user_id == user_id)
        )
        existing_style = result.scalar_one_or_none()
        
        if existing_style and existing_style.extraction_status == "completed":
            logger.info(f"Using cached writing style for user {user_id}")
            return json.loads(existing_style.extracted_style)
        
        # No cached style, need to extract from cover letter
        logger.info(f"Extracting writing style for user {user_id}")
        return await self.extract_and_store_style(user_id)
    
    async def extract_and_store_style(self, user_id: int) -> Dict[str, Any]:
        """
        Extract writing style from user's cover letter and store in writing_styles table.
        
        Args:
            user_id: User identifier
            
        Returns:
            Extracted writing style dictionary
            
        Raises:
            ValueError: If no active cover letter sample found
        """
        # Find user's active cover letter sample
        result = await self.db.execute(
            select(SampleDocumentModel).where(
                and_(
                    SampleDocumentModel.user_id == user_id,
                    SampleDocumentModel.document_type == "cover_letter",
                    SampleDocumentModel.is_active == True
                )
            ).order_by(SampleDocumentModel.created_at.desc())
        )
        
        sample = result.scalar_one_or_none()
        if not sample:
            raise ValueError(f"No active cover letter sample found for user {user_id}")
        
        # Extract writing style using regex analysis
        style_data = self._extract_style_from_text(sample.original_text)
        
        # Check if user already has a writing style record
        result = await self.db.execute(
            select(WritingStyleModel).where(WritingStyleModel.user_id == user_id)
        )
        existing_record = result.scalar_one_or_none()
        
        now = datetime.utcnow()
        confidence = self._calculate_confidence(sample.original_text)
        
        if existing_record:
            # Update existing record
            existing_record.extracted_style = json.dumps(style_data)
            existing_record.extraction_status = "completed"
            existing_record.extraction_model = "regex_analysis"
            existing_record.extraction_timestamp = now
            existing_record.extraction_confidence = confidence
            existing_record.source_sample_id = sample.id
            existing_record.updated_at = now
            
            await self.db.commit()
            await self.db.refresh(existing_record)
            
            logger.info(f"Updated writing style for user {user_id} with confidence {confidence}")
        else:
            # Create new record
            writing_style = WritingStyleModel(
                id=str(uuid.uuid4()),
                user_id=user_id,
                extracted_style=json.dumps(style_data),
                extraction_status="completed",
                extraction_model="regex_analysis", 
                extraction_timestamp=now,
                extraction_confidence=confidence,
                source_sample_id=sample.id
            )
            
            self.db.add(writing_style)
            await self.db.commit()
            await self.db.refresh(writing_style)
            
            logger.info(f"Stored writing style for user {user_id} from sample {sample.id} with confidence {confidence}")
        
        return style_data
    
    async def force_re_extract_style(self, user_id: int) -> Dict[str, Any]:
        """
        Force re-extraction of writing style (ignores cached version).
        
        Args:
            user_id: User identifier
            
        Returns:
            Newly extracted writing style dictionary
        """
        logger.info(f"Force re-extracting writing style for user {user_id}")
        return await self.extract_and_store_style(user_id)
    
    def _extract_style_from_text(self, text: str) -> Dict[str, Any]:
        """Extract writing style characteristics from text using regex analysis."""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Clean and prepare text
        cleaned_text = self._clean_text(text)
        sentences = self._split_sentences(cleaned_text)
        words = cleaned_text.lower().split()
        word_count = len(words)
        
        if word_count < 10:
            raise ValueError("Text too short for analysis (minimum 10 words)")
        
        # Analyze different aspects
        vocabulary_analysis = self._analyze_vocabulary(words, text)
        tone_analysis = self._analyze_tone_and_formality(text, sentences)
        structure_analysis = self._analyze_sentence_structure(sentences)
        language_patterns = self._analyze_language_patterns(text, words)
        content_approach = self._analyze_content_approach(text, sentences)
        
        return {
            "writing_style": {
                **vocabulary_analysis,
                **tone_analysis,
                **structure_analysis
            },
            "language_patterns": language_patterns,
            "content_approach": content_approach
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean text for analysis."""
        # Remove extra whitespace and normalize
        text = re.sub(r'\\s+', ' ', text.strip())
        # Remove email signatures and common artifacts
        text = re.sub(r'(Best regards|Sincerely|Thank you)[^\\n]*$', '', text, flags=re.IGNORECASE)
        return text
    
    def _split_sentences(self, text: str) -> list:
        """Split text into sentences."""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _analyze_vocabulary(self, words: list, original_text: str) -> Dict[str, Any]:
        """Analyze vocabulary complexity and level."""
        # Count syllables approximation (vowel groups)
        total_syllables = sum(max(1, len(re.findall(r'[aeiou]+', word.lower()))) for word in words)
        avg_syllables = total_syllables / len(words)
        
        # Vocabulary complexity score (1-10)
        complexity_score = min(10, max(1, int(avg_syllables * 2)))
        
        # Determine vocabulary level
        if complexity_score <= 3:
            vocab_level = "basic"
        elif complexity_score <= 6:
            vocab_level = "professional"
        else:
            vocab_level = "advanced"
        
        return {
            "vocabulary_level": vocab_level,
            "vocabulary_complexity_score": complexity_score
        }
    
    def _analyze_tone_and_formality(self, text: str, sentences: list) -> Dict[str, Any]:
        """Analyze tone and formality level."""
        text_lower = text.lower()
        
        # Formality indicators
        formal_indicators = sum(1 for phrase in self.FORMAL_CONNECTORS if phrase in text_lower)
        informal_indicators = sum(1 for phrase in self.INFORMAL_CONNECTORS if phrase in text_lower)
        
        # Contractions count (informal indicator)
        contractions = len(re.findall(r"\\b\\w+'\\w+\\b", text))
        
        # Personal pronouns (first person usage)
        first_person_count = len(re.findall(r'\\b(I|my|me|myself)\\b', text, re.IGNORECASE))
        first_person_frequency = "frequent" if first_person_count > 3 else "moderate" if first_person_count > 0 else "rare"
        
        # Determine formality level (1-5 scale)
        formality_score = 3  # Start neutral
        formality_score += formal_indicators * 0.5
        formality_score -= informal_indicators * 0.3
        formality_score -= contractions * 0.2
        formality_level = max(1, min(5, int(formality_score)))
        
        # Determine tone
        if formality_level >= 4:
            tone = "formal"
        elif formality_level >= 3:
            tone = "semi-formal"
        else:
            tone = "casual"
        
        return {
            "tone": tone,
            "formality_level": formality_level,
            "first_person_frequency": first_person_frequency
        }
    
    def _analyze_sentence_structure(self, sentences: list) -> Dict[str, Any]:
        """Analyze sentence structure patterns."""
        if not sentences:
            return {
                "sentence_structure": "simple",
                "avg_sentence_length": "short",
                "active_voice_ratio": 0.0
            }
        
        sentence_lengths = [len(sentence.split()) for sentence in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        
        # Categorize average sentence length
        if avg_length < 10:
            length_category = "short"
        elif avg_length < 20:
            length_category = "medium"
        else:
            length_category = "long"
        
        # Analyze sentence variety
        length_variance = len(set(range(min(sentence_lengths)//5, max(sentence_lengths)//5 + 1)))
        structure = "varied" if length_variance > 2 else "consistent"
        
        # Active vs passive voice (simplified analysis)
        active_count = sum(1 for sentence in sentences 
                          if not re.search(r'\\b(was|were|been|being)\\s+\\w+ed\\b', sentence.lower()))
        active_ratio = active_count / len(sentences) if sentences else 0
        
        return {
            "sentence_structure": structure,
            "avg_sentence_length": length_category,
            "active_voice_ratio": round(active_ratio, 2)
        }
    
    def _analyze_language_patterns(self, text: str, words: list) -> Dict[str, Any]:
        """Analyze specific language patterns and word choices."""
        text_lower = text.lower()
        
        # Find action verbs
        action_verbs = []
        for verb_set, verbs in [
            ("strong", self.STRONG_ACTION_VERBS),
            ("moderate", self.MODERATE_ACTION_VERBS), 
            ("weak", self.WEAK_ACTION_VERBS)
        ]:
            found_verbs = [verb for verb in verbs if verb in text_lower]
            action_verbs.extend(found_verbs)
        
        # Find technical terms
        technical_terms = [term for term in self.TECHNICAL_TERMS if term.lower() in text_lower]
        
        # Find connector phrases
        formal_connectors = [conn for conn in self.FORMAL_CONNECTORS if conn in text_lower]
        informal_connectors = [conn for conn in self.INFORMAL_CONNECTORS if conn in text_lower]
        connector_phrases = formal_connectors + informal_connectors
        
        # Find emphasis words (very, extremely, highly, etc.)
        emphasis_words = re.findall(r'\\b(very|extremely|highly|significantly|tremendously|exceptionally)\\b', text_lower)
        
        # Find qualification language (maybe, perhaps, might, etc.)
        qualification_language = re.findall(r'\\b(maybe|perhaps|might|possibly|potentially|somewhat)\\b', text_lower)
        
        return {
            "action_verbs": list(set(action_verbs))[:10],  # Top 10 unique
            "technical_terms": list(set(technical_terms))[:10],
            "connector_phrases": list(set(connector_phrases))[:5],
            "emphasis_words": list(set(emphasis_words)),
            "qualification_language": list(set(qualification_language))
        }
    
    def _analyze_content_approach(self, text: str, sentences: list) -> Dict[str, Any]:
        """Analyze how content is structured and presented."""
        text_lower = text.lower()
        
        # Storytelling style
        story_indicators = len(re.findall(r'\\b(when|while|during|after|before|then|next|finally)\\b', text_lower))
        achievement_indicators = len(re.findall(r'\\b(achieved|accomplished|delivered|increased|improved|reduced|saved)\\b', text_lower))
        
        if achievement_indicators > story_indicators:
            storytelling_style = "achievement-focused"
        elif story_indicators > 2:
            storytelling_style = "narrative"
        else:
            storytelling_style = "direct"
        
        # Evidence style (metrics vs descriptions)
        metric_indicators = len(re.findall(r'\\b\\d+(%|percent|\\$|k|million|billion|years?|months?)\\b', text))
        descriptive_indicators = len(re.findall(r'\\b(excellent|great|good|effective|successful|strong)\\b', text_lower))
        
        if metric_indicators > descriptive_indicators:
            evidence_style = "quantitative"
        elif descriptive_indicators > metric_indicators:
            evidence_style = "qualitative"
        else:
            evidence_style = "mixed"
        
        # Example integration
        example_indicators = len(re.findall(r'\\b(such as|for example|including|like|e\\.g\\.)\\b', text_lower))
        if example_indicators > 2:
            example_integration = "example_heavy"
        elif example_indicators > 0:
            example_integration = "integrated_naturally"
        else:
            example_integration = "minimal_examples"
        
        # Industry language usage
        industry_terms_count = len([term for term in self.TECHNICAL_TERMS if term.lower() in text_lower])
        if industry_terms_count > 5:
            industry_usage = "heavy"
        elif industry_terms_count > 2:
            industry_usage = "moderate"
        else:
            industry_usage = "minimal"
        
        return {
            "storytelling_style": storytelling_style,
            "evidence_style": evidence_style,
            "example_integration": example_integration,
            "industry_language_usage": industry_usage
        }
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score based on text length and quality."""
        word_count = len(text.split())
        
        # Base confidence on text length
        if word_count < 50:
            base_confidence = 0.4
        elif word_count < 150:
            base_confidence = 0.7
        elif word_count < 300:
            base_confidence = 0.8
        else:
            base_confidence = 0.9
        
        # Adjust for text quality indicators
        if len(re.findall(r'[.!?]', text)) < 3:  # Very few sentences
            base_confidence *= 0.8
        
        return round(base_confidence, 2)