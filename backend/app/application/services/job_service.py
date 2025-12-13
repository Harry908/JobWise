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
            
        Raises:
            ValueError: If source is 'mock' (mock jobs should not be saved to database)
        """
        # Prevent mock jobs from being saved to database
        if source == "mock":
            raise ValueError("Mock jobs cannot be saved to database. Use browse_jobs() to access mock data.")
        
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
    
    async def get_by_id(self, job_id: str, user_id: int) -> Optional[Job]:
        """Get job by ID.
        
        Args:
            job_id: Job ID
            user_id: User ID for authorization
            
        Returns:
            Job entity or None
        """
        return await self.repository.get_by_id(job_id, user_id)
    
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
        
        # Extract description (skip first 2 lines: title and company)
        # Keep location if it's on line 3, or include from line 3 onwards
        description_start_idx = 2
        if len(lines) > 2 and location and lines[2] == location:
            description_start_idx = 3
        
        description = '\n'.join(lines[description_start_idx:]) if len(lines) > description_start_idx else raw_text
        
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
        """Extract keywords from job text with comprehensive 2024-2025 tech stack coverage.
        
        Args:
            text: Job text
            
        Returns:
            List of keywords (lowercase)
        """
        # Comprehensive tech keywords based on 2024-2025 industry trends
        tech_keywords = [
            # Top Programming Languages (2024-2025 most demanded)
            "javascript", "typescript", "python", "java", "c#", "c++", "php", "ruby", "go", "golang",
            "rust", "swift", "kotlin", "scala", "r", "perl", "bash", "powershell", "shell",
            "objective-c", "dart", "lua", "groovy", "elixir", "haskell", "clojure", "f#",
            # Short codes (need special handling)
            "js", "ts",
            
            # Markup & Data
            "sql", "nosql", "html", "html5", "css", "css3", "xml", "json", "yaml", "toml", "markdown",
            
            # Frontend Frameworks & Libraries (React ecosystem dominant)
            "react", "react.js", "reactjs", "vue", "vue.js", "vuejs", "angular", "angularjs", 
            "svelte", "sveltekit", "next.js", "nextjs", "nuxt", "nuxt.js", "gatsby", "remix",
            "solid.js", "solidjs", "preact", "lit", "web components", "alpine.js",
            "jquery", "backbone", "ember", "meteor",
            
            # CSS Frameworks & Tools
            "tailwind", "tailwindcss", "bootstrap", "material-ui", "mui", "ant design", "chakra ui",
            "styled-components", "sass", "scss", "less", "postcss", "emotion",
            
            # State Management
            "redux", "mobx", "zustand", "recoil", "jotai", "pinia", "vuex", "context api", "xstate",
            
            # Backend Frameworks (Node.js, Python, Java, .NET)
            "node.js", "nodejs", "express", "express.js", "nest.js", "nestjs", "koa", "fastify", "hapi",
            "django", "flask", "fastapi", "pyramid", "tornado", "aiohttp", "quart",
            "spring", "spring boot", "spring cloud", "micronaut", "quarkus", "play framework",
            ".net", "dotnet", "asp.net", "asp.net core", "blazor", "entity framework", "ef core",
            "rails", "ruby on rails", "sinatra", "laravel", "symfony", "codeigniter", "cakephp",
            "gin", "echo", "fiber", "beego", "actix", "rocket", "axum", "warp",
            
            # API Technologies
            "rest", "restful", "rest api", "graphql", "grpc", "grpc-web", "websocket", "soap",
            "openapi", "swagger", "postman", "insomnia", "api gateway", "webhooks",
            
            # Mobile Development
            "ios", "android", "react native", "flutter", "xamarin", "ionic", "cordova", "phonegap",
            "swiftui", "jetpack compose", "mobile development", "native development",
            
            # Cloud Platforms (AWS dominance, Azure, GCP)
            "aws", "amazon web services", "azure", "microsoft azure", "gcp", "google cloud platform",
            "google cloud", "ibm cloud", "oracle cloud", "digitalocean", "linode", "heroku", "vercel",
            "netlify", "cloudflare", "firebase", "supabase", "amplify",
            
            # AWS Services
            "ec2", "s3", "lambda", "rds", "dynamodb", "cloudfront", "route 53", "elastic beanstalk",
            "eks", "ecs", "fargate", "sns", "sqs", "api gateway", "cloudwatch", "iam",
            
            # Azure Services
            "azure functions", "azure devops", "azure sql", "cosmos db", "azure storage",
            "azure kubernetes service", "aks", "azure active directory", "azure ad",
            
            # GCP Services
            "compute engine", "cloud functions", "cloud run", "cloud storage", "bigquery",
            "cloud sql", "firestore", "cloud pub/sub", "gke", "google kubernetes engine",
            
            # Container & Orchestration
            "docker", "docker compose", "podman", "kubernetes", "k8s", "helm", "rancher",
            "openshift", "nomad", "docker swarm", "containerd",
            
            # CI/CD & DevOps Tools
            "jenkins", "github actions", "gitlab ci", "gitlab ci/cd", "circleci", "travis ci",
            "bamboo", "teamcity", "azure pipelines", "codepipeline", "harness", "spinnaker",
            "argo cd", "argocd", "flux", "tekton",
            
            # Infrastructure as Code
            "terraform", "terragrunt", "pulumi", "cloudformation", "aws cdk", "bicep", "arm templates",
            "ansible", "puppet", "chef", "saltstack", "crossplane",
            
            # Databases - SQL
            "postgresql", "postgres", "mysql", "mariadb", "microsoft sql server", "sql server",
            "mssql", "oracle", "oracle database", "db2", "sqlite", "cockroachdb", "yugabytedb",
            
            # Databases - NoSQL
            "mongodb", "cassandra", "couchbase", "couchdb", "dynamodb", "redis", "memcached",
            "neo4j", "arangodb", "orientdb", "ravendb", "rethinkdb",
            
            # Search & Analytics
            "elasticsearch", "opensearch", "solr", "algolia", "meilisearch", "typesense",
            "splunk", "datadog", "new relic", "prometheus", "grafana", "kibana",
            
            # Message Queues & Streaming
            "kafka", "apache kafka", "rabbitmq", "activemq", "zeromq", "nats", "redis streams",
            "amazon sqs", "amazon sns", "google pub/sub", "azure service bus", "pulsar",
            
            # Data Processing & Big Data
            "spark", "apache spark", "hadoop", "apache hadoop", "flink", "storm", "airflow",
            "luigi", "prefect", "dagster", "dbt", "snowflake", "databricks", "redshift",
            "bigquery", "presto", "trino", "hive",
            
            # Machine Learning & AI (Rapidly growing 2024-2025)
            "machine learning", "ml", "deep learning", "ai", "artificial intelligence",
            "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "pandas", "numpy",
            "opencv", "hugging face", "transformers", "langchain", "llamaindex", "openai",
            "gpt", "llm", "large language models", "generative ai", "mlops", "mlflow",
            "kubeflow", "sagemaker", "vertex ai", "azure ml",
            
            # Testing Frameworks
            "jest", "mocha", "chai", "jasmine", "cypress", "playwright", "selenium", "webdriver",
            "pytest", "unittest", "nose", "junit", "testng", "mockito", "jest", "vitest",
            "testing library", "enzyme", "karma", "protractor", "puppeteer",
            
            # Build Tools & Bundlers
            "webpack", "vite", "rollup", "parcel", "esbuild", "swc", "turbopack", "gulp",
            "grunt", "maven", "gradle", "ant", "make", "cmake", "bazel", "nx", "turborepo",
            
            # Version Control
            "git", "github", "gitlab", "bitbucket", "subversion", "svn", "mercurial", "perforce",
            "git flow", "github flow", "trunk-based development",
            
            # Project Management & Collaboration
            "jira", "confluence", "trello", "asana", "monday.com", "notion", "clickup",
            "slack", "microsoft teams", "teams", "discord", "zoom", "linear",
            
            # IDEs & Editors
            "vs code", "visual studio code", "visual studio", "intellij", "intellij idea",
            "pycharm", "webstorm", "phpstorm", "rider", "goland", "eclipse", "netbeans",
            "sublime text", "atom", "vim", "neovim", "emacs", "jupyter", "jupyter notebook",
            "colab", "google colab",
            
            # Methodologies & Practices (2024-2025 focus)
            "agile", "scrum", "kanban", "lean", "devops", "devsecops", "sre", "site reliability engineering",
            "ci/cd", "continuous integration", "continuous deployment", "continuous delivery",
            "tdd", "test-driven development", "bdd", "behavior-driven development",
            "pair programming", "mob programming", "code review", "refactoring",
            
            # Architecture & Patterns
            "microservices", "monolith", "serverless", "event-driven", "cqrs", "event sourcing",
            "domain-driven design", "ddd", "clean architecture", "hexagonal architecture",
            "mvvm", "mvc", "mvp", "solid", "design patterns", "distributed systems",
            
            # Programming Paradigms
            "oop", "object-oriented programming", "functional programming", "reactive programming",
            "procedural programming", "declarative programming", "imperative programming",
            
            # Security
            "oauth", "oauth2", "openid connect", "oidc", "jwt", "saml", "ssl", "tls", "https",
            "encryption", "authentication", "authorization", "rbac", "abac", "zero trust",
            "penetration testing", "vulnerability assessment", "owasp", "sast", "dast",
            
            # Observability & Monitoring
            "prometheus", "grafana", "datadog", "new relic", "dynatrace", "appdynamics",
            "splunk", "elastic stack", "elk stack", "jaeger", "zipkin", "opentelemetry",
            "logging", "monitoring", "tracing", "metrics", "alerting",
            
            # Web Servers & Proxies
            "nginx", "apache", "apache httpd", "tomcat", "iis", "caddy", "traefik", "envoy",
            "haproxy", "varnish", "squid",
            
            # Operating Systems & Platforms
            "linux", "unix", "ubuntu", "debian", "centos", "rhel", "red hat", "fedora",
            "arch linux", "windows", "windows server", "macos", "freebsd",
            
            # Blockchain & Web3 (Growing 2024-2025)
            "blockchain", "ethereum", "solidity", "web3", "smart contracts", "bitcoin",
            "hyperledger", "polygon", "solana", "nft", "defi",
            
            # Emerging Technologies
            "edge computing", "iot", "internet of things", "5g", "quantum computing",
            "ar", "vr", "augmented reality", "virtual reality", "metaverse",
            
            # Data Formats & Protocols
            "protobuf", "protocol buffers", "avro", "thrift", "messagepack", "cbor",
            "http", "http/2", "http/3", "tcp", "udp", "mqtt", "amqp",
            
            # Analytics & Business Intelligence
            "analytics", "data analytics", "business intelligence", "bi", "tableau",
            "power bi", "looker", "metabase", "superset", "qlik", "sisense",
            "google analytics", "mixpanel", "amplitude", "segment"
        ]
        
        text_lower = text.lower()
        found_keywords = set()  # Use set to avoid duplicates
        
        # Sort by length (descending) to match longer phrases first (e.g., "spring boot" before "spring")
        tech_keywords.sort(key=len, reverse=True)
        
        for keyword in tech_keywords:
            # Special handling for keywords with special chars
            if '#' in keyword or '++' in keyword:
                # For C# and C++, use simpler contains check (case-sensitive for these)
                if keyword in text or keyword.upper() in text or keyword.lower() in text:
                    found_keywords.add(keyword)
            elif keyword in ['r', 'c', 'd', 'f', 'go']:
                # Single letter languages need exact word boundary + context check
                # Only match if it appears as a standalone word with likely context
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower, re.IGNORECASE):
                    # Additional context check for single letters to reduce false positives
                    context_patterns = {
                        'r': r'\b(r\s+language|r\s+programming|ggplot|dplyr|tidyverse|cran)\b',
                        'c': r'\b(c\s+language|c\s+programming|ansi\s+c|iso\s+c)\b',
                        'd': r'\b(d\s+language|d\s+programming|dlang)\b',
                        'f': r'\b(f#|f\s+sharp)\b',
                        'go': r'\b(golang|go\s+lang)\b'
                    }
                    if keyword in context_patterns and re.search(context_patterns[keyword], text_lower, re.IGNORECASE):
                        found_keywords.add(keyword)
                    elif keyword == 'go' and re.search(r'\bgolang\b', text_lower, re.IGNORECASE):
                        found_keywords.add('go')
            else:
                # Use word boundaries for regular keywords
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower, re.IGNORECASE):
                    found_keywords.add(keyword)
        
        return sorted(list(found_keywords))  # Return sorted list
    
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
        
        # Look for requirements section with various heading patterns
        in_requirements = False
        requirement_headers = [
            'requirement', 'qualifications', 'required', 'must have',
            'what you\'ll need', 'what we\'re looking for', 'you have',
            'minimum qualifications', 'basic qualifications', 'you should have'
        ]
        
        # Track if we found a requirements section with a header
        found_header_section = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check for requirements section headers
            if any(header in line_lower for header in requirement_headers):
                in_requirements = True
                found_header_section = True
                continue
            
            if in_requirements:
                # Stop at next major section
                stop_keywords = ['benefit', 'perks', 'we offer', 'why join', 'about us', 
                                'about the company', 'responsibilities', 'what you\'ll do']
                if any(keyword in line_lower for keyword in stop_keywords):
                    in_requirements = False
                    continue
                
                # Extract requirement lines
                if line.strip() and not line.startswith('#'):
                    # Remove bullet points and clean
                    cleaned = re.sub(r'^[\-\*•\d+\.\)]\s*', '', line.strip())
                    if cleaned and len(cleaned) > 5:  # Avoid very short lines
                        requirements.append(cleaned)
        
        # If no requirements found with headers, look for unlabeled requirements at the end
        # These often appear after benefit descriptions or EEO statements
        if not found_header_section or len(requirements) < 2:
            requirements = await self._extract_unlabeled_requirements(lines)
        
        return requirements[:15]  # Limit to 15 requirements
    
    async def _extract_unlabeled_requirements(self, lines: List[str]) -> List[str]:
        """Extract requirements that don't have a section header.
        
        Args:
            lines: Lines of job text
            
        Returns:
            List of requirement strings
        """
        requirements = []
        
        # Find where long prose paragraphs end and short requirement lines begin
        # Typically requirements are at the end and are shorter, more concise lines
        potential_reqs_start = -1
        
        for i in range(len(lines) - 1, max(len(lines) - 15, 0), -1):  # Look at last 15 lines
            line = lines[i].strip()
            if not line or len(line) < 10:  # Skip empty or very short lines
                continue
            
            # Strong requirement indicators (things that must be met)
            strong_requirement_indicators = [
                'degree', 'bachelor', 'master', 'phd', 'bs/', 'ba/', 'ms/', 'ma/',
                'years of experience', 'years experience', 'proficient in', 
                'certification', 'certified', 'eligible to work', 'authorized to work',
                'vaccination', 'vaccinated', 'must have', 'required:', 'require:',
                'minimum', 'at least'
            ]
            
            # Words that indicate this is NOT a requirement
            exclusion_indicators = [
                'we offer', 'you will receive', 'you\'ll get', 'opportunity to',
                'work with', 'learn more', 'see our', 'click here', 'apply now',
                'join our', 'our team', 'we are', 'about us', 'http', '@',
                'write software', 'build', 'create', 'develop'  # These are responsibilities
            ]
            
            line_lower = line.lower()
            
            # Skip lines with exclusion indicators
            if any(indicator in line_lower for indicator in exclusion_indicators):
                continue
            
            # Check if line has strong requirement indicators
            has_strong_req = any(indicator in line_lower for indicator in strong_requirement_indicators)
            
            # If line has strong requirement indicators and isn't too long, likely a requirement
            if len(line) < 300 and has_strong_req:
                # Clean and add
                cleaned = re.sub(r'^[\-\*•\d+\.\)]\s*', '', line)
                if cleaned and cleaned not in requirements:
                    requirements.insert(0, cleaned)  # Insert at beginning to maintain order
        
        return requirements
    
    async def _extract_benefits(self, text: str) -> List[str]:
        """Extract job benefits from text.
        
        Args:
            text: Job text
            
        Returns:
            List of benefits
        """
        benefits = []
        lines = text.split('\n')
        
        # Look for benefits section with various heading patterns
        in_benefits = False
        benefit_headers = [
            'benefit', 'perks', 'we offer', 'what we offer', 'why join',
            'what you\'ll get', 'compensation and benefits', 'rewards',
            'what you get'
        ]
        
        lines_after_benefits_header = 0
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check for benefits section headers
            if any(header in line_lower for header in benefit_headers):
                in_benefits = True
                lines_after_benefits_header = 0
                continue
            
            if in_benefits:
                lines_after_benefits_header += 1
                
                # Stop at next major section or when we hit requirements-like content
                stop_keywords = ['requirement', 'qualifications', 'responsibilities', 
                                'about the role', 'what you\'ll do', 'equal opportunity',
                                'you should', 'you must', 'you have', 'relocation']
                
                # Strong requirement indicators that should stop benefits extraction
                requirement_indicators = [
                    'bs/', 'ba/', 'ms/', 'ma/', 'bachelor', 'master', 'phd',
                    'years of experience', 'years experience',
                    'certified', 'certification required', 'eligible to work',
                    'authorized to work', 'must have', 'vaccination', 'visa sponsorship'
                ]
                
                # Stop if we see requirement indicators OR if we've gone 10+ lines past header
                # (to avoid pulling in unrelated content)
                has_req_indicator = any(indicator in line_lower for indicator in requirement_indicators)
                has_stop_keyword = any(keyword in line_lower for keyword in stop_keywords)
                
                if has_req_indicator or has_stop_keyword or lines_after_benefits_header > 10:
                    in_benefits = False
                    continue
                
                # Extract benefit lines - must be substantial text
                if line.strip() and not line.startswith('#') and len(line.strip()) > 20:
                    # Remove bullet points and clean
                    cleaned = re.sub(r'^[\-\*•\d+\.\)]\s*', '', line.strip())
                    if cleaned and 'http' not in cleaned.lower():
                        benefits.append(cleaned)
        
        return benefits[:15]  # Limit to 15 benefits
    
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
