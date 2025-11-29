"""Job service for business logic and text parsing."""

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from app.domain.entities.job import Job
from app.infrastructure.repositories.job_repository import JobRepository


class JobService:
    """Service for job-related business logic."""
    
    def __init__(self, repository: JobRepository):
        """Initialize service with repository.
        
        Args:
            repository: Job repository instance
        """
        self.repository = repository
        self._mock_jobs_cache: Optional[List[Dict[str, Any]]] = None
    
    async def create_from_text(self, user_id: int, raw_text: str) -> Job:
        """Create job by parsing raw text.
        
        Args:
            user_id: User ID
            raw_text: Raw job description text
            
        Returns:
            Created Job entity
        """
        # Parse text to extract job details
        parsed_data = await self._parse_job_text(raw_text)
        
        # Create job data dictionary
        job_data = {
            "user_id": user_id,
            "source": "user_created",
            "raw_text": raw_text,
            **parsed_data
        }
        
        # Create job via repository
        return await self.repository.create(job_data)
    
    async def create_from_url(self, user_id: int, url: str) -> Job:
        """Create job by fetching from URL.
        
        Args:
            user_id: User ID
            url: Job posting URL
            
        Returns:
            Created Job entity
        """
        # Fetch job data from URL
        fetched_data = await self._fetch_job_from_url(url)
        
        # Create job data dictionary
        job_data = {
            "user_id": user_id,
            "source": "url_import",
            "raw_text": url,
            **fetched_data
        }
        
        # Create job via repository
        return await self.repository.create(job_data)
    
    async def create_structured(
        self,
        user_id: int,
        source: str,
        title: str,
        company: str,
        location: Optional[str] = None,
        description: Optional[str] = None,
        requirements: Optional[List[str]] = None,
        benefits: Optional[List[str]] = None,
        salary_range: Optional[str] = None,
        remote: bool = False,
        employment_type: str = "full_time",
        status: str = "active"
    ) -> Job:
        """Create job from structured data (already parsed).
        
        Args:
            user_id: User ID
            source: Job source
            title: Job title
            company: Company name
            location: Job location
            description: Job description
            requirements: List of requirements
            benefits: List of benefits
            salary_range: Salary range
            remote: Remote work option
            employment_type: Employment type
            status: Job status
            
        Returns:
            Created Job entity
        """
        # Parse keywords from description and title
        text_for_keywords = f"{title} {company}"
        if description:
            text_for_keywords += f" {description}"
        
        keywords = await self._parse_keywords(text_for_keywords)
        
        # Create job data dictionary
        job_data = {
            "user_id": user_id,
            "source": source,
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "requirements": requirements or [],
            "benefits": benefits or [],
            "parsed_keywords": keywords,
            "salary_range": salary_range,
            "remote": remote,
            "employment_type": employment_type,
            "status": status,
            "raw_text": None  # No raw text for structured input
        }
        
        # Create job via repository
        return await self.repository.create(job_data)
    
    async def get_user_jobs(
        self,
        user_id: int,
        status: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Job]:
        """Get jobs for a specific user with filters.
        
        Args:
            user_id: User ID
            status: Filter by status
            source: Filter by source
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of Job entities
        """
        return await self.repository.get_user_jobs(
            user_id=user_id,
            status=status,
            source=source,
            limit=limit,
            offset=offset
        )
    
    async def browse_jobs(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> List[Job]:
        """Browse mock job listings from JSON file.
        
        Args:
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of Job entities from mock data
        """
        # Load mock jobs if not cached
        if self._mock_jobs_cache is None:
            self._mock_jobs_cache = await self._load_mock_jobs()
        
        # Apply pagination
        paginated_jobs = self._mock_jobs_cache[offset:offset + limit]
        
        # Convert to Job entities
        return [Job(**job_data) for job_data in paginated_jobs]
    
    async def count_browse_jobs(self) -> int:
        """Get total count of browse jobs.
        
        Returns:
            Total number of browse jobs
        """
        # Load mock jobs if not cached
        if self._mock_jobs_cache is None:
            self._mock_jobs_cache = await self._load_mock_jobs()
        
        return len(self._mock_jobs_cache)
    
    async def count_user_jobs(
        self,
        user_id: int,
        status: Optional[str] = None,
        source: Optional[str] = None
    ) -> int:
        """Get total count of user's jobs.
        
        Args:
            user_id: User ID
            status: Filter by status
            source: Filter by source
            
        Returns:
            Total number of user's jobs
        """
        # For now, get all jobs and count them
        # TODO: Add efficient count method to repository
        jobs = await self.repository.get_user_jobs(
            user_id=user_id,
            status=status,
            source=source,
            limit=1000,  # Large limit to get all
            offset=0
        )
        return len(jobs)
    
    async def get_by_id(self, job_id: str) -> Optional[Job]:
        """Get job by ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job entity or None
        """
        return await self.repository.get_by_id(job_id)
    
    async def update_job(self, job_id: str, **kwargs) -> Optional[Job]:
        """Update job details.
        
        Args:
            job_id: Job ID
            **kwargs: Fields to update
            
        Returns:
            Updated Job entity or None
        """
        return await self.repository.update(job_id, **kwargs)
    
    async def delete_job(self, job_id: str) -> bool:
        """Delete a job.
        
        Args:
            job_id: Job ID
            
        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete(job_id)
    
    async def _parse_job_text(self, raw_text: str) -> Dict[str, Any]:
        """Parse raw job text to extract structured data.
        
        Args:
            raw_text: Raw job description text
            
        Returns:
            Dictionary of parsed job fields
        """
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        
        # Extract basic fields
        title = lines[0] if len(lines) > 0 else "Untitled Position"
        company = lines[1] if len(lines) > 1 else "Unknown Company"
        location = await self._extract_location(raw_text)
        
        # Extract parsed data
        keywords = await self._parse_keywords(raw_text)
        requirements = await self._extract_requirements(raw_text)
        benefits = await self._extract_benefits(raw_text)
        salary_range = await self._extract_salary(raw_text)
        remote = await self._detect_remote(raw_text)
        
        # Extract description (everything after line 3)
        description = '\n'.join(lines[3:]) if len(lines) > 3 else raw_text
        
        return {
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "parsed_keywords": keywords,
            "requirements": requirements,
            "benefits": benefits,
            "salary_range": salary_range,
            "remote": remote,
            "status": "active"
        }
    
    async def _fetch_job_from_url(self, url: str) -> Dict[str, Any]:
        """Fetch job data from URL.
        
        Note: Simplified implementation - real version would use web scraping
        
        Args:
            url: Job posting URL
            
        Returns:
            Dictionary of job fields
        """
        # Basic implementation for URL parsing
        # Production version would use web scraping or job board APIs
        return {
            "title": "Job from URL",
            "company": "Unknown Company",
            "location": None,
            "description": f"Job imported from {url}",
            "parsed_keywords": [],
            "requirements": [],
            "benefits": [],
            "salary_range": None,
            "remote": False
        }
    
    async def _parse_keywords(self, text: str) -> List[str]:
        """Extract keywords from job text.
        
        Args:
            text: Job text
            
        Returns:
            List of keywords (lowercase)
        """
        # Common tech keywords to search for
        tech_keywords = [
            "python", "java", "javascript", "typescript", "react", "vue", "angular",
            "node.js", "fastapi", "django", "flask", "spring", "dotnet",
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
            "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "git", "ci/cd", "jenkins", "github", "gitlab",
            "agile", "scrum", "api", "rest", "graphql", "microservices"
        ]
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in tech_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    async def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from text.
        
        Args:
            text: Job text
            
        Returns:
            Location string or None
        """
        # Look for location patterns in first few lines
        lines = text.split('\n')[:5]
        
        for line in lines:
            # Match patterns like "Seattle, WA", "San Francisco, CA (Remote)", etc.
            location_match = re.search(
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})',
                line
            )
            if location_match:
                return location_match.group(1)
        
        return None
    
    async def _extract_requirements(self, text: str) -> List[str]:
        """Extract job requirements from text.
        
        Args:
            text: Job text
            
        Returns:
            List of requirements
        """
        requirements = []
        lines = text.split('\n')
        
        # Look for requirements section
        in_requirements = False
        for line in lines:
            line_lower = line.lower()
            
            if 'requirement' in line_lower or 'qualifications' in line_lower:
                in_requirements = True
                continue
            
            if in_requirements:
                # Stop at next major section
                if any(keyword in line_lower for keyword in ['benefit', 'salary', 'about', 'responsibilities']):
                    break
                
                # Extract requirement lines
                if line.strip() and not line.startswith('#'):
                    # Remove bullet points and clean
                    cleaned = re.sub(r'^[\-\*•]\s*', '', line.strip())
                    if cleaned:
                        requirements.append(cleaned)
        
        return requirements[:10]  # Limit to 10 requirements
    
    async def _extract_benefits(self, text: str) -> List[str]:
        """Extract job benefits from text.
        
        Args:
            text: Job text
            
        Returns:
            List of benefits
        """
        benefits = []
        lines = text.split('\n')
        
        # Look for benefits section
        in_benefits = False
        for line in lines:
            line_lower = line.lower()
            
            if 'benefit' in line_lower or 'perks' in line_lower:
                in_benefits = True
                continue
            
            if in_benefits:
                # Stop at next major section
                if any(keyword in line_lower for keyword in ['requirement', 'salary', 'about', 'responsibilities']):
                    break
                
                # Extract benefit lines
                if line.strip() and not line.startswith('#'):
                    # Remove bullet points and clean
                    cleaned = re.sub(r'^[\-\*•]\s*', '', line.strip())
                    if cleaned:
                        benefits.append(cleaned)
        
        return benefits[:10]  # Limit to 10 benefits
    
    async def _extract_salary(self, text: str) -> Optional[str]:
        """Extract salary range from text.
        
        Args:
            text: Job text
            
        Returns:
            Salary range string (e.g., "120000-180000") or None
        """
        # Pattern 1: $120,000 - $180,000
        pattern1 = r'\$(\d{1,3}(?:,\d{3})*)\s*-\s*\$(\d{1,3}(?:,\d{3})*)'
        match1 = re.search(pattern1, text)
        if match1:
            low = match1.group(1).replace(',', '')
            high = match1.group(2).replace(',', '')
            return f"{low}-{high}"
        
        # Pattern 2: 100k-150k
        pattern2 = r'(\d+)k\s*-\s*(\d+)k'
        match2 = re.search(pattern2, text, re.IGNORECASE)
        if match2:
            low = int(match2.group(1)) * 1000
            high = int(match2.group(2)) * 1000
            return f"{low}-{high}"
        
        return None
    
    async def _detect_remote(self, text: str) -> bool:
        """Detect if position is remote from text.
        
        Args:
            text: Job text
            
        Returns:
            True if remote work detected
        """
        text_lower = text.lower()
        remote_keywords = ['remote', 'work from home', 'wfh', 'hybrid', 'distributed']
        
        return any(keyword in text_lower for keyword in remote_keywords)
    
    async def _load_mock_jobs(self) -> List[Dict[str, Any]]:
        """Load mock jobs from JSON file.
        
        Returns:
            List of job dictionaries
        """
        # Path to mock jobs file
        mock_file = Path(__file__).parent.parent.parent.parent / "data" / "mock_jobs.json"
        
        if not mock_file.exists():
            # Return empty list if file doesn't exist
            return []
        
        # Load JSON data
        with open(mock_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract job list from JSON structure
        jobs_data = data.get("tech_jobs", [])
        
        # Create mutable copies and ensure each job has required fields
        processed_jobs = []
        for job in jobs_data:
            # Create mutable copy
            job_copy = dict(job)
            
            if "id" not in job_copy:
                job_copy["id"] = f"mock_{uuid.uuid4().hex[:12]}"
            if "user_id" not in job_copy:
                job_copy["user_id"] = None  # Mock jobs have no owner
            if "status" not in job_copy:
                job_copy["status"] = "active"
            if "created_at" not in job_copy:
                job_copy["created_at"] = datetime.utcnow().isoformat()
            if "updated_at" not in job_copy:
                job_copy["updated_at"] = datetime.utcnow().isoformat()
            
            processed_jobs.append(job_copy)
        
        return processed_jobs
