# Job API Redesign - Simple CRUD with Text Parsing

## Overview

The Job API provides simple CRUD operations for job descriptions. It accepts either:
1. **Raw text** (user copy-pastes from job website)
2. **Structured JSON** (from external API results)

Both are processed and stored as the same unified `JobDescription` object.

---

## Database Model

### Single Table: `job_descriptions`

```sql
CREATE TABLE job_descriptions (
    id              VARCHAR(36) PRIMARY KEY DEFAULT (uuid()),
    user_id         VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Core fields (extracted from text or provided)
    title           VARCHAR(200) NOT NULL,
    company         VARCHAR(200) NOT NULL,
    location        VARCHAR(200),
    description     TEXT NOT NULL,
    requirements    JSON DEFAULT '[]',
    benefits        JSON DEFAULT '[]',

    -- Metadata
    job_type        VARCHAR(50),
    experience_level VARCHAR(50),
    salary_min      INTEGER,
    salary_max      INTEGER,
    salary_currency VARCHAR(3) DEFAULT 'USD',
    remote_work     VARCHAR(20),

    -- Source tracking
    source          VARCHAR(20) NOT NULL,  -- 'user_created' or 'saved_external'
    external_id     VARCHAR(100),          -- If from external API
    external_url    VARCHAR(500),          -- Application URL

    -- Original text (for reference)
    raw_text        TEXT,                  -- Original pasted text (if applicable)

    -- Status
    status          VARCHAR(20) DEFAULT 'active',

    -- Timestamps
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),

    INDEX idx_user_jobs (user_id, status, created_at DESC),
    INDEX idx_title_company (title, company)
);
```

---

## DTOs

### CreateJobDescriptionRequest

```python
class CreateJobDescriptionRequest(BaseModel):
    """
    Create job description from raw text or structured data.

    The API accepts either:
    1. raw_text: Plain text job posting (will be parsed)
    2. Structured fields: Pre-parsed job data

    If raw_text is provided, it takes precedence and other fields
    are used as fallback/override.
    """

    # Option 1: Raw text (user copy-paste)
    raw_text: Optional[str] = Field(None, max_length=20000)

    # Option 2: Structured data (or override for raw_text)
    title: Optional[str] = Field(None, max_length=200)
    company: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=10000)
    requirements: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)

    # Optional metadata
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    salary_currency: str = Field(default="USD")
    remote_work: Optional[str] = None

    # Source info
    source: Literal["user_created", "saved_external"] = "user_created"
    external_id: Optional[str] = None
    external_url: Optional[str] = None

    @model_validator(mode='after')
    def validate_data(self):
        """Ensure either raw_text or (title + company + description) provided"""
        if not self.raw_text:
            if not (self.title and self.company and self.description):
                raise ValueError(
                    "Must provide either raw_text OR (title, company, description)"
                )
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "description": "User copy-paste example",
                    "value": {
                        "raw_text": """Senior Software Engineer

TechCorp Inc.
San Francisco, CA (Hybrid)

We are seeking a Senior Software Engineer to join our backend team...

Requirements:
- 5+ years Python experience
- FastAPI or Django
- PostgreSQL, Redis

Benefits:
- Competitive salary
- Health insurance
""",
                        "source": "user_created"
                    }
                },
                {
                    "description": "Structured data from external API",
                    "value": {
                        "title": "Senior Software Engineer",
                        "company": "TechCorp Inc.",
                        "location": "San Francisco, CA",
                        "description": "We are seeking...",
                        "requirements": ["5+ years Python", "FastAPI"],
                        "benefits": ["Health insurance", "401k"],
                        "job_type": "full-time",
                        "remote_work": "hybrid",
                        "source": "saved_external",
                        "external_id": "indeed_12345",
                        "external_url": "https://indeed.com/job/12345"
                    }
                }
            ]
        }
    )
```

### UpdateJobDescriptionRequest

```python
class UpdateJobDescriptionRequest(BaseModel):
    """Update job description (all fields optional)"""

    title: Optional[str] = Field(None, max_length=200)
    company: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=10000)
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    remote_work: Optional[str] = None
    status: Optional[Literal["active", "archived"]] = None
```

### JobDescriptionResponse

```python
class JobDescriptionResponse(BaseModel):
    """Job description response"""

    id: str
    user_id: str

    # Core fields
    title: str
    company: str
    location: Optional[str]
    description: str
    requirements: List[str]
    benefits: List[str]

    # Metadata
    job_type: Optional[str]
    experience_level: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    salary_currency: str
    remote_work: Optional[str]

    # Source
    source: str
    external_id: Optional[str]
    external_url: Optional[str]
    raw_text: Optional[str]

    # Status
    status: str

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

---

## API Endpoints (Pure CRUD)

### Base: `/api/v1/job-descriptions`

```python
# CREATE - Parse text or accept structured data
POST   /api/v1/job-descriptions
Request:  CreateJobDescriptionRequest
Response: JobDescriptionResponse (201)

# READ - List user's jobs
GET    /api/v1/job-descriptions
Query:  ?status=active&source=user_created&limit=20&offset=0
Response: {jobs: [], total, limit, offset, has_more} (200)

# READ - Get single job
GET    /api/v1/job-descriptions/{id}
Response: JobDescriptionResponse (200)

# UPDATE
PUT    /api/v1/job-descriptions/{id}
Request:  UpdateJobDescriptionRequest
Response: JobDescriptionResponse (200)

# DELETE
DELETE /api/v1/job-descriptions/{id}
Response: 204 No Content
```

---

## Implementation

### 1. Text Parser Service

```python
class JobDescriptionParser:
    """Parse raw job posting text into structured data"""

    def parse(self, raw_text: str) -> dict:
        """
        Parse raw text into structured job description.

        Uses simple pattern matching and NLP (future: could use LLM).

        Returns dict with: title, company, location, description,
                          requirements, benefits, etc.
        """
        lines = raw_text.strip().split('\n')

        # Simple extraction (enhance later with regex/NLP/LLM)
        result = {
            "title": self._extract_title(lines),
            "company": self._extract_company(lines),
            "location": self._extract_location(lines),
            "description": self._extract_description(raw_text),
            "requirements": self._extract_section(raw_text, "requirements"),
            "benefits": self._extract_section(raw_text, "benefits"),
            "job_type": self._extract_job_type(raw_text),
            "experience_level": self._extract_experience_level(raw_text),
            "remote_work": self._extract_remote_work(raw_text),
        }

        return {k: v for k, v in result.items() if v is not None}

    def _extract_title(self, lines: List[str]) -> Optional[str]:
        """First non-empty line is usually the title"""
        for line in lines:
            clean = line.strip()
            if clean and len(clean) > 3:
                return clean
        return None

    def _extract_company(self, lines: List[str]) -> Optional[str]:
        """Second line often contains company name"""
        if len(lines) > 1:
            return lines[1].strip()
        return None

    # ... more extraction methods
```

### 2. Repository

```python
class JobDescriptionRepository:
    """Repository for job descriptions"""

    def __init__(self, session: AsyncSession, parser: JobDescriptionParser):
        self.session = session
        self.parser = parser

    async def create(
        self,
        user_id: str,
        data: CreateJobDescriptionRequest
    ) -> JobDescriptionResponse:
        """Create job description from raw text or structured data"""

        # Parse raw text if provided
        if data.raw_text:
            parsed = self.parser.parse(data.raw_text)

            # Merge with provided structured data (structured data wins)
            job_data = {
                **parsed,  # Parsed from text
                **data.model_dump(exclude={"raw_text"}, exclude_none=True),  # Override
            }
            job_data["raw_text"] = data.raw_text
        else:
            # Use structured data directly
            job_data = data.model_dump(exclude_none=True)

        # Validate required fields after parsing
        if not job_data.get("title"):
            raise ValueError("Could not extract title from text")
        if not job_data.get("company"):
            raise ValueError("Could not extract company from text")
        if not job_data.get("description"):
            raise ValueError("Could not extract description from text")

        # Create database model
        job_desc = JobDescriptionModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            **job_data
        )

        self.session.add(job_desc)
        await self.session.commit()
        await self.session.refresh(job_desc)

        return JobDescriptionResponse.model_validate(job_desc)

    async def get_by_id(self, job_id: str) -> Optional[JobDescriptionResponse]:
        """Get job description by ID"""
        result = await self.session.execute(
            select(JobDescriptionModel).where(JobDescriptionModel.id == job_id)
        )
        job_desc = result.scalar_one_or_none()

        if job_desc:
            return JobDescriptionResponse.model_validate(job_desc)
        return None

    async def list_by_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[JobDescriptionResponse]:
        """List user's job descriptions with filters"""
        query = select(JobDescriptionModel).where(
            JobDescriptionModel.user_id == user_id
        )

        if status:
            query = query.where(JobDescriptionModel.status == status)
        if source:
            query = query.where(JobDescriptionModel.source == source)

        query = query.order_by(JobDescriptionModel.created_at.desc())
        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        jobs = result.scalars().all()

        return [JobDescriptionResponse.model_validate(j) for j in jobs]

    async def count_by_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        source: Optional[str] = None
    ) -> int:
        """Count user's job descriptions"""
        query = select(func.count(JobDescriptionModel.id)).where(
            JobDescriptionModel.user_id == user_id
        )

        if status:
            query = query.where(JobDescriptionModel.status == status)
        if source:
            query = query.where(JobDescriptionModel.source == source)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def update(
        self,
        job_id: str,
        data: UpdateJobDescriptionRequest
    ) -> JobDescriptionResponse:
        """Update job description"""
        job_desc = await self.session.get(JobDescriptionModel, job_id)

        if not job_desc:
            raise ValueError("Job description not found")

        # Update fields
        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(job_desc, field, value)

        job_desc.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(job_desc)

        return JobDescriptionResponse.model_validate(job_desc)

    async def delete(self, job_id: str) -> bool:
        """Soft delete job description"""
        job_desc = await self.session.get(JobDescriptionModel, job_id)

        if not job_desc:
            return False

        job_desc.status = "deleted"
        job_desc.updated_at = datetime.utcnow()

        await self.session.commit()
        return True
```

### 3. API Router

```python
router = APIRouter(prefix="/job-descriptions", tags=["Job Descriptions"])


@router.post("/", response_model=JobDescriptionResponse, status_code=201)
async def create_job_description(
    request: CreateJobDescriptionRequest,
    current_user: User = Depends(get_current_user),
    repo: JobDescriptionRepository = Depends(get_repo)
):
    """
    Create job description from raw text or structured data.

    Accepts:
    1. raw_text: Plain text job posting (will be auto-parsed)
    2. Structured fields: Pre-parsed job details

    Use case 1 - User copy-paste:
    {
      "raw_text": "Senior Engineer\\nTechCorp\\nSan Francisco...",
      "source": "user_created"
    }

    Use case 2 - External API save:
    {
      "title": "Senior Engineer",
      "company": "TechCorp",
      "description": "...",
      "source": "saved_external",
      "external_id": "indeed_12345"
    }
    """
    try:
        job_desc = await repo.create(user_id=str(current_user.id), data=request)
        return job_desc
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create: {str(e)}")


@router.get("/", response_model=dict)
async def list_job_descriptions(
    status: Optional[str] = Query(None, pattern="^(active|archived)$"),
    source: Optional[str] = Query(None, pattern="^(user_created|saved_external)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    repo: JobDescriptionRepository = Depends(get_repo)
):
    """List user's job descriptions with optional filters"""
    jobs = await repo.list_by_user(
        user_id=str(current_user.id),
        status=status,
        source=source,
        limit=limit,
        offset=offset
    )
    total = await repo.count_by_user(str(current_user.id), status, source)

    return {
        "jobs": jobs,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit < total)
    }


@router.get("/{job_id}", response_model=JobDescriptionResponse)
async def get_job_description(
    job_id: str,
    current_user: User = Depends(get_current_user),
    repo: JobDescriptionRepository = Depends(get_repo)
):
    """Get job description details"""
    job = await repo.get_by_id(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")

    if job.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    return job


@router.put("/{job_id}", response_model=JobDescriptionResponse)
async def update_job_description(
    job_id: str,
    request: UpdateJobDescriptionRequest,
    current_user: User = Depends(get_current_user),
    repo: JobDescriptionRepository = Depends(get_repo)
):
    """Update job description"""
    job = await repo.get_by_id(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")

    if job.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    updated = await repo.update(job_id, request)
    return updated


@router.delete("/{job_id}", status_code=204)
async def delete_job_description(
    job_id: str,
    current_user: User = Depends(get_current_user),
    repo: JobDescriptionRepository = Depends(get_repo)
):
    """Delete job description"""
    job = await repo.get_by_id(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")

    if job.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    await repo.delete(job_id)
    return None
```

---

## Usage Examples

### 1. User Copy-Pastes Job from Website

```http
POST /api/v1/job-descriptions
Authorization: Bearer <token>

{
  "raw_text": "Senior Backend Engineer\n\nTechCorp Inc.\nRemote (US)\n\nWe are looking for an experienced backend engineer...\n\nRequirements:\n- 5+ years Python\n- FastAPI, PostgreSQL\n- AWS experience\n\nBenefits:\n- Health insurance\n- 401k matching",
  "source": "user_created"
}
```

**Response**:
```json
{
  "id": "uuid-here",
  "user_id": "user-uuid",
  "title": "Senior Backend Engineer",
  "company": "TechCorp Inc.",
  "location": "Remote (US)",
  "description": "We are looking for an experienced backend engineer...",
  "requirements": ["5+ years Python", "FastAPI, PostgreSQL", "AWS experience"],
  "benefits": ["Health insurance", "401k matching"],
  "remote_work": "remote",
  "source": "user_created",
  "raw_text": "Senior Backend Engineer...",
  "status": "active",
  "created_at": "2025-10-20T10:00:00Z",
  "updated_at": "2025-10-20T10:00:00Z"
}
```

### 2. User Saves Job from External API

```http
POST /api/v1/job-descriptions
Authorization: Bearer <token>

{
  "title": "Senior Backend Engineer",
  "company": "TechCorp Inc.",
  "location": "Remote (US)",
  "description": "We are looking for...",
  "requirements": ["5+ years Python", "FastAPI"],
  "job_type": "full-time",
  "remote_work": "remote",
  "source": "saved_external",
  "external_id": "indeed_67890",
  "external_url": "https://indeed.com/job/67890"
}
```

**Response**: Same structure as above, but with `source: "saved_external"`

### 3. List User's Jobs

```http
GET /api/v1/job-descriptions?status=active&limit=10
Authorization: Bearer <token>
```

**Response**:
```json
{
  "jobs": [/* array of JobDescriptionResponse */],
  "total": 25,
  "limit": 10,
  "offset": 0,
  "has_more": true
}
```

---

## Benefits

1. **Simple Interface**: Just 5 endpoints (POST, GET, GET/:id, PUT/:id, DELETE/:id)
2. **Flexible Input**: Accepts raw text OR structured data
3. **Auto-Parsing**: Converts unstructured text to structured data
4. **Unified Storage**: Both user-created and saved-external stored the same way
5. **Clear Ownership**: All jobs belong to a user
6. **Easy Testing**: Simple CRUD operations

## Summary

The redesigned Job API is a **pure CRUD API** that:
- Accepts raw text and parses it into structured job descriptions
- Handles both user-created jobs and jobs saved from external APIs
- Stores everything in a single unified `job_descriptions` table
- Provides simple list, get, create, update, delete operations
- No complex search, filtering, or analysis (those belong elsewhere)

This is clean, focused, and easy to maintain!
