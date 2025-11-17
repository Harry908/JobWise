"""
Writing Style Service - In-memory extraction (V3.0).

Extracts writing style characteristics from sample cover letter text
without making LLM calls. Uses regex and string analysis.
"""

import logging
import re
from typing import Dict, Any
from collections import Counter

logger = logging.getLogger(__name__)


class WritingStyleService:
    """
    Service for extracting writing style from sample text.
    
    Performs in-memory analysis without LLM calls for <1s performance.
    """
    
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
        "subsequently", "accordingly", "thus", "hence", "therefore"
    }
    
    CASUAL_CONNECTORS = {
        "also", "plus", "but", "so", "and then", "or", "because", "like"
    }
    
    def extract_style(self, sample_text: str) -> Dict[str, Any]:
        """
        Extract writing style from sample text.
        
        Args:
            sample_text: Cover letter or writing sample
            
        Returns:
            Writing style configuration dict
        """
        if not sample_text or len(sample_text.strip()) < 50:
            raise ValueError("Sample text too short for style extraction (minimum 50 characters)")
        
        # Clean text
        text = sample_text.strip()
        
        # Extract components
        vocabulary = self._analyze_vocabulary(text)
        sentence_structure = self._analyze_sentences(text)
        tone = self._analyze_tone(text)
        language_patterns = self._extract_language_patterns(text)
        
        return {
            "writing_style": {
                "vocabulary_level": vocabulary["level"],
                "vocabulary_complexity_score": vocabulary["complexity_score"],
                "tone": tone["tone"],
                "formality_level": tone["formality_level"],
                "sentence_structure": sentence_structure["structure_type"],
                "avg_sentence_length": sentence_structure["avg_length_category"],
                "active_voice_ratio": sentence_structure["active_voice_ratio"],
                "first_person_frequency": sentence_structure["first_person_frequency"]
            },
            "language_patterns": language_patterns,
            "content_approach": {
                "storytelling_style": self._detect_storytelling_style(text),
                "evidence_style": self._detect_evidence_style(text),
                "example_integration": "integrated_naturally",
                "industry_language_usage": "moderate"
            }
        }
    
    def _analyze_vocabulary(self, text: str) -> Dict[str, Any]:
        """Analyze vocabulary complexity."""
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words:
            return {"level": "professional", "complexity_score": 5}
        
        # Average word length as proxy for complexity
        avg_word_length = sum(len(w) for w in words) / len(words)
        
        # Count sophisticated words (>8 letters)
        sophisticated_words = [w for w in words if len(w) > 8]
        sophistication_ratio = len(sophisticated_words) / len(words)
        
        # Determine complexity score (1-10)
        if avg_word_length < 4.5:
            complexity_score = 3
            level = "conversational"
        elif avg_word_length < 5.5:
            complexity_score = 5
            level = "professional"
        elif avg_word_length < 6.5:
            complexity_score = 7
            level = "professional"
        else:
            complexity_score = 9
            level = "academic"
        
        # Adjust by sophistication ratio
        if sophistication_ratio > 0.15:
            complexity_score = min(10, complexity_score + 1)
        
        return {
            "level": level,
            "complexity_score": complexity_score,
            "avg_word_length": round(avg_word_length, 2),
            "sophistication_ratio": round(sophistication_ratio, 2)
        }
    
    def _analyze_sentences(self, text: str) -> Dict[str, Any]:
        """Analyze sentence structure."""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if not sentences:
            return {
                "structure_type": "varied",
                "avg_length_category": "medium",
                "active_voice_ratio": 0.7,
                "first_person_frequency": "moderate"
            }
        
        # Calculate average sentence length
        total_words = sum(len(s.split()) for s in sentences)
        avg_sentence_length = total_words / len(sentences) if sentences else 0
        
        # Categorize length
        if avg_sentence_length < 12:
            length_category = "short"
        elif avg_sentence_length < 20:
            length_category = "medium"
        else:
            length_category = "long"
        
        # Detect active voice (simple heuristic: subject before verb)
        active_voice_count = 0
        for sentence in sentences:
            # Active voice often starts with subject (I, we, name, company)
            if re.match(r'^(I|We|My|Our|The\s+\w+)\s+\w+(ed|s|ing)\b', sentence, re.IGNORECASE):
                active_voice_count += 1
        
        active_voice_ratio = active_voice_count / len(sentences) if sentences else 0.7
        
        # Count first-person pronouns
        first_person_words = re.findall(r'\b(I|me|my|mine|we|us|our|ours)\b', text, re.IGNORECASE)
        first_person_ratio = len(first_person_words) / len(text.split())
        
        if first_person_ratio < 0.02:
            first_person_frequency = "rare"
        elif first_person_ratio < 0.05:
            first_person_frequency = "moderate"
        else:
            first_person_frequency = "frequent"
        
        # Determine structure type based on variation
        word_counts = [len(s.split()) for s in sentences]
        if len(set(word_counts)) > len(sentences) * 0.6:
            structure_type = "varied"
        elif avg_sentence_length < 15:
            structure_type = "simple"
        else:
            structure_type = "complex"
        
        return {
            "structure_type": structure_type,
            "avg_length_category": length_category,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "active_voice_ratio": round(active_voice_ratio, 2),
            "first_person_frequency": first_person_frequency
        }
    
    def _analyze_tone(self, text: str) -> Dict[str, Any]:
        """Analyze tone and formality."""
        text_lower = text.lower()
        
        # Count formal vs casual connectors
        formal_count = sum(1 for connector in self.FORMAL_CONNECTORS if connector in text_lower)
        casual_count = sum(1 for connector in self.CASUAL_CONNECTORS if connector in text_lower)
        
        # Detect enthusiasm markers
        exclamations = text.count('!')
        enthusiasm_words = len(re.findall(r'\b(excited|thrilled|passionate|eager|enthusiastic)\b', text_lower))
        
        # Determine formality (1-10 scale)
        if formal_count > casual_count * 2:
            formality_level = 8
            tone = "formal"
        elif formal_count > casual_count:
            formality_level = 6
            tone = "semi-formal"
        else:
            formality_level = 4
            tone = "semi-formal"
        
        # Adjust tone based on enthusiasm
        if enthusiasm_words > 2 or exclamations > 1:
            tone = "enthusiastic"
        elif re.search(r'\b(authoritative|expertise|proven|demonstrate)\b', text_lower):
            tone = "authoritative"
        
        return {
            "tone": tone,
            "formality_level": formality_level,
            "formal_connector_count": formal_count,
            "enthusiasm_markers": enthusiasm_words + exclamations
        }
    
    def _extract_language_patterns(self, text: str) -> Dict[str, Any]:
        """Extract specific language patterns."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Extract action verbs
        action_verbs = []
        for verb_set, category in [
            (self.STRONG_ACTION_VERBS, "strong"),
            (self.MODERATE_ACTION_VERBS, "moderate"),
            (self.WEAK_ACTION_VERBS, "weak")
        ]:
            found = [v for v in verb_set if v in words]
            action_verbs.extend(found[:5])  # Limit to 5 per category
        
        # Extract technical terms (words with numbers, capitals, or technical indicators)
        technical_terms = list(set(
            re.findall(r'\b(?:[A-Z]{2,}|\w+(?:Script|SQL|API|SDK|ML|AI|Python|Java|React))\b', text)
        ))[:10]
        
        # Extract connector phrases
        connector_phrases = []
        for connector in list(self.FORMAL_CONNECTORS)[:5] + list(self.CASUAL_CONNECTORS)[:5]:
            if connector in text_lower:
                connector_phrases.append(connector)
        
        # Extract emphasis words
        emphasis_words = list(set(
            re.findall(r'\b(significantly|substantially|dramatically|effectively|successfully|proven|demonstrated)\b', text_lower)
        ))[:10]
        
        return {
            "action_verbs": action_verbs[:10],
            "technical_terms": technical_terms,
            "connector_phrases": connector_phrases[:10],
            "emphasis_words": emphasis_words,
            "qualification_language": self._extract_qualification_phrases(text)
        }
    
    def _extract_qualification_phrases(self, text: str) -> list:
        """Extract qualification/credibility phrases."""
        patterns = [
            r'proven track record',
            r'demonstrated ability',
            r'\d+ years of experience',
            r'expertise in',
            r'proficient in',
            r'skilled in',
            r'certified',
            r'award-winning'
        ]
        
        found = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            found.extend(matches)
        
        return list(set(found))[:10]
    
    def _detect_storytelling_style(self, text: str) -> str:
        """Detect storytelling approach."""
        text_lower = text.lower()
        
        # Achievement-focused: many metrics and results
        achievement_markers = len(re.findall(r'\b\d+%|\$\d+|increased|improved|reduced|grew\b', text_lower))
        
        # Narrative: temporal markers and story flow
        narrative_markers = len(re.findall(r'\bwhen|during|after|before|then|first|finally\b', text_lower))
        
        if achievement_markers > narrative_markers * 1.5:
            return "achievement-focused"
        elif narrative_markers > achievement_markers:
            return "narrative-driven"
        else:
            return "balanced"
    
    def _detect_evidence_style(self, text: str) -> str:
        """Detect how evidence is presented."""
        text_lower = text.lower()
        
        # Quantified: numbers and percentages
        quantified = len(re.findall(r'\b\d+(?:%|\s+percent|K|M|million|thousand)\b', text_lower))
        
        # Qualitative: descriptive adjectives
        qualitative = len(re.findall(r'\b(significant|substantial|comprehensive|extensive|notable)\b', text_lower))
        
        if quantified > 3:
            return "quantified_results"
        elif qualitative > quantified:
            return "qualitative_descriptors"
        else:
            return "mixed"


# FastAPI dependency
def get_writing_style_service() -> WritingStyleService:
    """
    FastAPI dependency for WritingStyleService injection.
    
    Usage:
        @app.post("/endpoint")
        async def endpoint(service: WritingStyleService = Depends(get_writing_style_service)):
            ...
    """
    return WritingStyleService()
