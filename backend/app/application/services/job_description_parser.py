"""Job Description Parser Service - Converts raw text to structured data"""

import re
from typing import Dict, List, Optional


class JobDescriptionParser:
    """
    Parse raw job posting text into structured data.

    Uses pattern matching and keyword extraction to identify
    job details from unstructured text.

    Future enhancements:
    - Use NLP libraries (spaCy, NLTK) for better extraction
    - Use LLM for highly accurate parsing
    """

    def parse(self, raw_text: str) -> Dict[str, any]:
        """
        Parse raw text into structured job description.

        Returns dict with: title, company, location, description,
                          requirements, benefits, etc.
        """
        if not raw_text or not raw_text.strip():
            return {}

        lines = raw_text.strip().split('\n')

        # Extract structured data
        result = {
            "title": self._extract_title(lines),
            "company": self._extract_company(lines),
            "location": self._extract_location(raw_text),
            "description": self._extract_description(raw_text),
            "requirements": self._extract_section(raw_text, "requirements"),
            "benefits": self._extract_section(raw_text, "benefits"),
            "job_type": self._extract_job_type(raw_text),
            "experience_level": self._extract_experience_level(raw_text),
            "remote_work": self._extract_remote_work(raw_text),
            "salary_min": None,  # TODO: Implement salary extraction
            "salary_max": None,
        }

        # Remove None values
        return {k: v for k, v in result.items() if v is not None}

    def _extract_title(self, lines: List[str]) -> Optional[str]:
        """
        First non-empty line is usually the job title.

        Example:
        "Senior Software Engineer" <- title
        "TechCorp Inc." <- company
        """
        for line in lines:
            clean = line.strip()
            if clean and len(clean) > 3 and not self._is_likely_company(clean):
                return clean
        return None

    def _extract_company(self, lines: List[str]) -> Optional[str]:
        """
        Second or third line often contains company name.
        Look for lines with "Inc", "LLC", "Corp", etc.
        """
        company_indicators = ['inc', 'llc', 'corp', 'ltd', 'company', 'co.']

        for i, line in enumerate(lines[1:5]):  # Check first few lines after title
            clean = line.strip().lower()

            # Check for company indicators
            if any(indicator in clean for indicator in company_indicators):
                return lines[i + 1].strip()

            # If line looks like a company (capitalized, not too long)
            if line.strip() and len(line.strip()) < 50:
                return line.strip()

        return None

    def _extract_location(self, text: str) -> Optional[str]:
        """
        Extract location from text.

        Patterns:
        - "City, State"
        - "City, Country"
        - "Remote"
        - "Hybrid"
        """
        # Remote patterns
        if re.search(r'\b(remote|work from home|wfh)\b', text, re.IGNORECASE):
            return "Remote"

        # City, State pattern (e.g., "San Francisco, CA")
        location_match = re.search(
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\b',
            text
        )
        if location_match:
            return f"{location_match.group(1)}, {location_match.group(2)}"

        # City, Country pattern (e.g., "London, UK")
        location_match = re.search(
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2,3})\b',
            text
        )
        if location_match:
            return f"{location_match.group(1)}, {location_match.group(2)}"

        return None

    def _extract_description(self, text: str) -> Optional[str]:
        """
        Extract main job description.

        This is usually the first substantial paragraph after title/company/location.
        """
        # Remove sections (Requirements, Benefits, etc.)
        sections_pattern = r'(?i)(requirements?|qualifications?|benefits?|responsibilities?|about):'
        parts = re.split(sections_pattern, text)

        if parts and len(parts[0]) > 100:
            # First part before any section is likely the description
            description = parts[0].strip()

            # Remove first few lines (title, company, location)
            lines = description.split('\n')
            if len(lines) > 3:
                description = '\n'.join(lines[3:]).strip()

            return description if description else None

        return None

    def _extract_section(self, text: str, section_name: str) -> List[str]:
        """
        Extract a specific section (Requirements, Benefits, etc.)

        Returns list of items from that section.
        """
        # Pattern to find section
        section_pattern = rf'(?i){section_name}:?\s*\n((?:[-•*]\s*.+\n?)+)'
        match = re.search(section_pattern, text)

        if match:
            section_text = match.group(1)

            # Extract bulleted items
            items = re.findall(r'[-•*]\s*(.+)', section_text)
            return [item.strip() for item in items if item.strip()]

        # Alternative: numbered list
        section_pattern_numbered = rf'(?i){section_name}:?\s*\n((?:\d+\.\s*.+\n?)+)'
        match = re.search(section_pattern_numbered, text)

        if match:
            section_text = match.group(1)
            items = re.findall(r'\d+\.\s*(.+)', section_text)
            return [item.strip() for item in items if item.strip()]

        return []

    def _extract_job_type(self, text: str) -> Optional[str]:
        """
        Extract job type (full-time, part-time, contract, etc.)
        """
        text_lower = text.lower()

        if 'full-time' in text_lower or 'full time' in text_lower:
            return 'full-time'
        elif 'part-time' in text_lower or 'part time' in text_lower:
            return 'part-time'
        elif 'contract' in text_lower:
            return 'contract'
        elif 'freelance' in text_lower:
            return 'freelance'
        elif 'internship' in text_lower:
            return 'internship'

        return None

    def _extract_experience_level(self, text: str) -> Optional[str]:
        """
        Extract experience level from text.

        Looks for patterns like:
        - "5+ years"
        - "Senior"
        - "Junior"
        - "Entry level"
        """
        text_lower = text.lower()

        # Check for explicit levels
        if 'senior' in text_lower or 'sr.' in text_lower:
            return 'senior'
        elif 'junior' in text_lower or 'jr.' in text_lower:
            return 'junior'
        elif 'entry' in text_lower or 'entry-level' in text_lower:
            return 'entry'
        elif 'mid' in text_lower or 'mid-level' in text_lower:
            return 'mid'
        elif 'lead' in text_lower or 'principal' in text_lower:
            return 'lead'

        # Check for years of experience
        years_match = re.search(r'(\d+)\+?\s*years?', text_lower)
        if years_match:
            years = int(years_match.group(1))
            if years >= 7:
                return 'senior'
            elif years >= 3:
                return 'mid'
            else:
                return 'junior'

        return None

    def _extract_remote_work(self, text: str) -> Optional[str]:
        """
        Extract remote work policy.

        Returns: remote, hybrid, or onsite
        """
        text_lower = text.lower()

        if 'hybrid' in text_lower:
            return 'hybrid'
        elif 'remote' in text_lower or 'work from home' in text_lower:
            return 'remote'
        elif 'on-site' in text_lower or 'onsite' in text_lower or 'in-office' in text_lower:
            return 'onsite'

        return None

    def _is_likely_company(self, text: str) -> bool:
        """Check if text looks like a company name"""
        company_keywords = ['inc', 'llc', 'corp', 'ltd', 'company', 'co.', 'corporation']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in company_keywords)
