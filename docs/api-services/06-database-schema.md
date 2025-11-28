# JobWise Database Schema

**Version**: 3.0
**Database**: SQLite (Development), PostgreSQL (Production)
**ORM**: SQLAlchemy 2.0 (Async)
**Last Updated**: November 2025

---

## Overview

JobWise uses a relational database with 10 core tables organized into three functional groups:

1. **User & Authentication** (1 table): User accounts and authentication
2. **Profile Management** (4 tables): Master resume profiles with experiences, education, and projects
3. **Job & Generation** (5 tables): Job postings, AI generation tracking, and content optimization

**Total Tables**: 10
**Database Technology**: SQLAlchemy ORM with async support
**Migration Tool**: Alembic

---

## Database Technology Stack

### Development
- **Database**: SQLite 3.x
- **Driver**: aiosqlite (async SQLite)
- **Connection String**: `sqlite+aiosqlite:///./jobwise.db`

### Production
- **Database**: PostgreSQL 14+
- **Driver**: asyncpg (async PostgreSQL)
- **Connection String**: `postgresql+asyncpg://user:pass@host:5432/dbname`

### ORM Configuration
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base

Base = declarative_base()

engine = create_async_engine(
    "sqlite+aiosqlite:///./jobwise.db",
    echo=True,  # Log SQL queries in development
)
```

---

## Entity Relationship Diagram

```
┌─────────────┐
│    users    │
└──────┬──────┘
       │
       ├───────────────────────────────────────┐
       │                                       │
       │ (1:N)                                 │ (1:1)
       ▼                                       ▼
┌──────────────────┐                  ┌──────────────────┐
│ master_profiles  │                  │ writing_styles   │
└────────┬─────────┘                  └──────────────────┘
         │                                     ▲
         │ (1:N)                               │
         ├──────────┬──────────┬───────────────┘
         ▼          ▼          ▼        (FK: source_sample_id)
    ┌────────┐ ┌─────────┐ ┌──────────┐
    │  exp.  │ │  edu.   │ │ projects │
    └────────┘ └─────────┘ └──────────┘

┌─────────────┐
│    users    │
└──────┬──────┘
       │
       │ (1:N)
       ├────────────┬──────────────────┬─────────────────────┐
       ▼            ▼                  ▼                     ▼
┌──────────┐  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐
│   jobs   │  │ generations │  │   samples    │  │ job_content_rankings │
└────┬─────┘  └──────┬──────┘  └──────────────┘  └──────────────────────┘
     │               │
     │ (1:N)         │ (FK: job_id, profile_id)
     └───────────────┘
```

---

## Table Schemas

### 1. users

**Purpose**: User authentication and account management

**Table Name**: `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | User ID |
| `email` | VARCHAR | UNIQUE, NOT NULL, INDEXED | User email (login) |
| `password_hash` | VARCHAR | NOT NULL | Bcrypt hashed password |
| `full_name` | VARCHAR | NOT NULL | User's full name |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account active status |
| `is_verified` | BOOLEAN | DEFAULT FALSE | Email verification status |
| `created_at` | TIMESTAMP | DEFAULT NOW | Account creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW, ON UPDATE NOW | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email`

**Relationships**:
- ONE-TO-MANY with `master_profiles`
- ONE-TO-MANY with `jobs`
- ONE-TO-MANY with `generations`
- ONE-TO-MANY with `sample_documents`
- ONE-TO-MANY with `job_content_rankings`
- ONE-TO-ONE with `writing_styles`

**Example Row**:
```json
{
  "id": 1,
  "email": "john.doe@example.com",
  "password_hash": "$2b$12$KIXl6zmP8ronWa.ZD9QZyO...",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": true,
  "created_at": "2025-11-15T10:30:00Z",
  "updated_at": "2025-11-15T10:30:00Z"
}
```

---

### 2. master_profiles

**Purpose**: Master resume profiles with personal info, summary, and skills

**Table Name**: `master_profiles`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR (UUID) | PRIMARY KEY | Profile ID |
| `user_id` | INTEGER | FOREIGN KEY (users.id), NOT NULL, INDEXED | Owner user ID |
| `personal_info` | JSON | NOT NULL | Personal information object |
| `professional_summary` | TEXT | NULLABLE | Original professional summary |
| `enhanced_professional_summary` | TEXT | NULLABLE | AI-enhanced summary (v3.0) |
| `enhancement_metadata` | JSON | DEFAULT {} | Enhancement metadata |
| `skills` | JSON | NOT NULL | Skills object (technical, soft, languages, certifications) |
| `custom_fields` | JSON | DEFAULT {} | Custom user fields |
| `created_at` | TIMESTAMP | DEFAULT NOW | Profile creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW, ON UPDATE NOW | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id`

**Relationships**:
- MANY-TO-ONE with `users`
- ONE-TO-MANY with `experiences` (cascade delete)
- ONE-TO-MANY with `education` (cascade delete)
- ONE-TO-MANY with `projects` (cascade delete)
- ONE-TO-MANY with `generations`

**JSON Field Structures**:

**personal_info**:
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-123-4567",
  "location": "Seattle, WA",
  "linkedin": "https://linkedin.com/in/johndoe",
  "github": "https://github.com/johndoe",
  "website": "https://johndoe.com"
}
```

**skills**:
```json
{
  "technical": ["Python", "FastAPI", "React", "AWS"],
  "soft": ["Leadership", "Communication", "Problem Solving"],
  "languages": [
    {"name": "English", "proficiency": "native"},
    {"name": "Spanish", "proficiency": "conversational"}
  ],
  "certifications": [
    {
      "name": "AWS Solutions Architect",
      "issuer": "Amazon",
      "date_obtained": "2023-01-15",
      "credential_id": "AWS-SA-123"
    }
  ]
}
```

**enhancement_metadata**:
```json
{
  "model": "llama-3.3-70b-versatile",
  "timestamp": "2025-11-15T10:35:00Z",
  "confidence": 0.92,
  "improvements": ["stronger action verbs", "quantified achievements"]
}
```

---

### 3. experiences

**Purpose**: Work experience history

**Table Name**: `experiences`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR (UUID) | PRIMARY KEY | Experience ID |
| `profile_id` | VARCHAR (UUID) | FOREIGN KEY (master_profiles.id), NOT NULL, INDEXED | Profile ID |
| `title` | VARCHAR | NOT NULL | Job title |
| `company` | VARCHAR | NOT NULL | Company name |
| `location` | VARCHAR | NULLABLE | Work location |
| `start_date` | VARCHAR | NOT NULL | Start date (ISO format: YYYY-MM-DD) |
| `end_date` | VARCHAR | NULLABLE | End date (null for current) |
| `is_current` | BOOLEAN | DEFAULT FALSE | Currently working flag |
| `description` | TEXT | NULLABLE | Original job description |
| `achievements` | JSON | NULLABLE | List of achievements |
| `enhanced_description` | TEXT | NULLABLE | AI-enhanced description (v3.0) |
| `enhancement_metadata` | JSON | DEFAULT {} | Enhancement metadata |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `profile_id`

**Relationships**:
- MANY-TO-ONE with `master_profiles` (cascade delete)

**JSON Field Structures**:

**achievements**:
```json
[
  "Led team of 5 engineers in microservices migration",
  "Reduced API response time by 60%",
  "Implemented CI/CD pipeline reducing deployment time from 2h to 15min"
]
```

**enhancement_metadata**:
```json
{
  "model": "llama-3.3-70b-versatile",
  "timestamp": "2025-11-15T10:40:00Z",
  "improvements": ["added metrics", "stronger action verbs", "quantified impact"]
}
```

---

### 4. education

**Purpose**: Educational background

**Table Name**: `education`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR (UUID) | PRIMARY KEY | Education ID |
| `profile_id` | VARCHAR (UUID) | FOREIGN KEY (master_profiles.id), NOT NULL, INDEXED | Profile ID |
| `institution` | VARCHAR | NOT NULL | School/university name |
| `degree` | VARCHAR | NOT NULL | Degree type (BS, MS, PhD, etc.) |
| `field_of_study` | VARCHAR | NOT NULL | Major/field of study |
| `start_date` | VARCHAR | NOT NULL | Start date (ISO format) |
| `end_date` | VARCHAR | NOT NULL | Graduation date |
| `gpa` | FLOAT | NULLABLE | Grade point average |
| `honors` | JSON | NULLABLE | List of honors/awards |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `profile_id`

**Relationships**:
- MANY-TO-ONE with `master_profiles` (cascade delete)

**JSON Field Structures**:

**honors**:
```json
[
  "Magna Cum Laude",
  "Dean's List (4 semesters)",
  "Outstanding CS Student Award 2016"
]
```

---

### 5. projects

**Purpose**: Personal and professional projects

**Table Name**: `projects`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR (UUID) | PRIMARY KEY | Project ID |
| `profile_id` | VARCHAR (UUID) | FOREIGN KEY (master_profiles.id), NOT NULL, INDEXED | Profile ID |
| `name` | VARCHAR | NOT NULL | Project name |
| `description` | TEXT | NOT NULL | Original project description |
| `technologies` | JSON | NULLABLE | List of technologies used |
| `url` | VARCHAR | NULLABLE | Project URL (GitHub, demo, etc.) |
| `start_date` | VARCHAR | NOT NULL | Start date (ISO format) |
| `end_date` | VARCHAR | NULLABLE | End date (null for ongoing) |
| `enhanced_description` | TEXT | NULLABLE | AI-enhanced description (v3.0) |
| `enhancement_metadata` | JSON | DEFAULT {} | Enhancement metadata |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `profile_id`

**Relationships**:
- MANY-TO-ONE with `master_profiles` (cascade delete)

**JSON Field Structures**:

**technologies**:
```json
["Flutter", "FastAPI", "PostgreSQL", "Docker", "AWS Lambda"]
```

**enhancement_metadata**:
```json
{
  "model": "llama-3.3-70b-versatile",
  "timestamp": "2025-11-15T10:45:00Z",
  "improvements": ["added technical depth", "quantified impact", "highlighted innovation"]
}
```

---

### 6. jobs

**Purpose**: Job postings (saved, scraped, or API-sourced)

**Table Name**: `jobs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR (UUID) | PRIMARY KEY | Job ID |
| `user_id` | INTEGER | FOREIGN KEY (users.id), NULLABLE, INDEXED | Owner user ID (null for public jobs) |
| `source` | VARCHAR | NOT NULL, INDEXED | Job source (user_created, indeed, linkedin, mock) |
| `title` | VARCHAR(200) | NOT NULL | Job title |
| `company` | VARCHAR(200) | NOT NULL | Company name |
| `location` | VARCHAR(200) | NULLABLE | Job location |
| `description` | TEXT | NULLABLE | Full job description |
| `raw_text` | TEXT | NULLABLE | Original pasted/scraped text |
| `parsed_keywords` | JSON | NULLABLE | Extracted keywords |
| `requirements` | JSON | NULLABLE | Job requirements list |
| `benefits` | JSON | NULLABLE | Job benefits list |
| `salary_range` | VARCHAR | NULLABLE | Salary information |
| `remote` | BOOLEAN | DEFAULT FALSE | Remote work flag |
| `employment_type` | VARCHAR | DEFAULT 'full_time' | full_time, part_time, contract, temporary, internship |
| `status` | VARCHAR | DEFAULT 'active', INDEXED | active, archived, draft |
| `application_status` | VARCHAR | DEFAULT 'not_applied', INDEXED | not_applied, applied, interview, offer, rejected |
| `created_at` | TIMESTAMP | DEFAULT NOW, INDEXED | Job creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW, ON UPDATE NOW | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id`
- INDEX on `source`
- INDEX on `status`
- INDEX on `application_status`
- INDEX on `created_at`

**Relationships**:
- MANY-TO-ONE with `users`
- ONE-TO-MANY with `generations`
- ONE-TO-MANY with `job_content_rankings`

**JSON Field Structures**:

**parsed_keywords**:
```json
["Python", "FastAPI", "AWS", "Docker", "microservices", "API design", "CI/CD"]
```

**requirements**:
```json
[
  "5+ years Python experience",
  "Strong knowledge of FastAPI or similar frameworks",
  "Experience with AWS services (Lambda, S3, DynamoDB)",
  "Excellent communication skills"
]
```

**benefits**:
```json
[
  "Competitive salary $120k-$160k",
  "Full health/dental/vision insurance",
  "401k with 5% match",
  "Unlimited PTO",
  "Remote-first culture"
]
```

---

### 7. generations

**Purpose**: AI document generation tracking

**Table Name**: `generations`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR (UUID) | PRIMARY KEY | Generation ID |
| `user_id` | INTEGER | FOREIGN KEY (users.id), NOT NULL, INDEXED | Owner user ID |
| `profile_id` | VARCHAR (UUID) | FOREIGN KEY (master_profiles.id), NOT NULL, INDEXED | Profile used |
| `job_id` | VARCHAR (UUID) | FOREIGN KEY (jobs.id), NOT NULL, INDEXED | Job targeted |
| `document_type` | VARCHAR | NOT NULL | 'resume' or 'cover_letter' |
| `status` | VARCHAR | DEFAULT 'pending', INDEXED | pending, generating, completed, failed, cancelled |
| `current_stage` | INTEGER | DEFAULT 0 | Current pipeline stage (0-2) |
| `total_stages` | INTEGER | DEFAULT 2 | Total pipeline stages |
| `stage_name` | VARCHAR | NULLABLE | Current stage name |
| `stage_description` | TEXT | NULLABLE | Current stage description |
| `error_message` | TEXT | NULLABLE | Error details if failed |
| `options` | TEXT | NULLABLE | Generation options (JSON as TEXT) |
| `result` | TEXT | NULLABLE | Generated document (JSON as TEXT) |
| `tokens_used` | INTEGER | DEFAULT 0 | LLM tokens consumed |
| `generation_time` | FLOAT | NULLABLE | Generation time in seconds |
| `user_custom_prompt` | TEXT | NULLABLE | User custom instructions (v3.0) |
| `created_at` | TIMESTAMP | DEFAULT NOW, INDEXED | Generation request timestamp |
| `started_at` | TIMESTAMP | NULLABLE | Processing start timestamp |
| `completed_at` | TIMESTAMP | NULLABLE | Completion timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW, ON UPDATE NOW | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id`
- INDEX on `profile_id`
- INDEX on `job_id`
- INDEX on `status`
- INDEX on `created_at`

**Relationships**:
- MANY-TO-ONE with `users`
- MANY-TO-ONE with `master_profiles`
- MANY-TO-ONE with `jobs`

**JSON Field Structures**:

**options** (stored as TEXT):
```json
{
  "max_experiences": 5,
  "max_projects": 3,
  "include_summary": true,
  "tone": "professional",
  "length": "medium"
}
```

**result** (stored as TEXT):
```json
{
  "content_text": "John Doe\nSenior Software Engineer\n\nPROFESSIONAL SUMMARY...",
  "ats_score": 87.5,
  "metadata": {
    "experiences_included": 5,
    "projects_included": 3,
    "word_count": 487
  }
}
```

---

### 8. writing_styles (v3.0)

**Purpose**: User's extracted writing style from cover letter analysis

**Table Name**: `writing_styles`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR (UUID) | PRIMARY KEY | Writing style ID |
| `user_id` | INTEGER | FOREIGN KEY (users.id), UNIQUE, NOT NULL, INDEXED | Owner user ID (1:1) |
| `extracted_style` | JSON | NOT NULL | Complete style analysis |
| `extraction_status` | VARCHAR | DEFAULT 'pending', NOT NULL | pending, completed, failed |
| `extraction_model` | VARCHAR | NULLABLE | Model used for extraction |
| `extraction_timestamp` | TIMESTAMP | NULLABLE | When style was extracted |
| `extraction_confidence` | FLOAT | NULLABLE | Confidence score (0.0-1.0) |
| `source_sample_id` | VARCHAR (UUID) | FOREIGN KEY (sample_documents.id), NULLABLE | Source sample reference |
| `created_at` | TIMESTAMP | DEFAULT NOW, NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW, ON UPDATE NOW, NOT NULL | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `user_id` (one writing style per user)

**Relationships**:
- ONE-TO-ONE with `users`
- MANY-TO-ONE with `sample_documents`

**JSON Field Structures**:

**extracted_style**:
```json
{
  "tone": "professional_warm",
  "formality_level": 0.75,
  "sentence_structure": {
    "avg_words_per_sentence": 18,
    "compound_sentence_ratio": 0.35,
    "uses_contractions": false
  },
  "vocabulary": {
    "technical_density": 0.28,
    "action_verb_preference": ["spearheaded", "orchestrated", "architected"],
    "transition_phrases": ["Furthermore", "Additionally", "Building on this"]
  },
  "paragraph_structure": {
    "opening_style": "direct_statement",
    "uses_topic_sentences": true,
    "avg_sentences_per_paragraph": 4
  },
  "signature_phrases": [
    "I am passionate about",
    "I look forward to contributing"
  ]
}
```

---

### 9. sample_documents (v3.0)

**Purpose**: Text-only storage for user-uploaded sample documents

**Table Name**: `sample_documents`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR (UUID) | PRIMARY KEY | Sample document ID |
| `user_id` | INTEGER | FOREIGN KEY (users.id), NOT NULL, INDEXED | Owner user ID |
| `document_type` | VARCHAR | NOT NULL, INDEXED | 'resume' or 'cover_letter' |
| `original_filename` | VARCHAR(255) | NULLABLE | Original filename |
| `upload_timestamp` | TIMESTAMP | DEFAULT NOW, NOT NULL | Upload timestamp |
| `original_text` | TEXT | NOT NULL | Complete document text content |
| `word_count` | INTEGER | NULLABLE | Word count |
| `character_count` | INTEGER | NULLABLE | Character count |
| `line_count` | INTEGER | NULLABLE | Line count |
| `is_active` | BOOLEAN | DEFAULT TRUE, NOT NULL | Active status |
| `archived_at` | TIMESTAMP | NULLABLE | Archive timestamp |
| `created_at` | TIMESTAMP | DEFAULT NOW, NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW, ON UPDATE NOW, NOT NULL | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id`
- INDEX on `document_type`

**Relationships**:
- MANY-TO-ONE with `users`
- ONE-TO-MANY with `writing_styles` (via `source_sample_id`)

**Business Logic**:
- When a new sample of type `cover_letter` is uploaded with `is_active=true`, previous samples of same type are set to `is_active=false`
- Only one active sample per document type per user
- Full text stored in database (no file system storage)

**Example Row**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "document_type": "cover_letter",
  "original_filename": "john_doe_cover_letter_2024.txt",
  "upload_timestamp": "2025-11-15T09:00:00Z",
  "original_text": "Dear Hiring Manager,\n\nI am writing to express my strong interest...",
  "word_count": 421,
  "character_count": 2847,
  "line_count": 42,
  "is_active": true,
  "archived_at": null,
  "created_at": "2025-11-15T09:00:00Z",
  "updated_at": "2025-11-15T09:00:00Z"
}
```

---

### 10. job_content_rankings (v3.0)

**Purpose**: Job-specific content rankings for AI generation optimization

**Table Name**: `job_content_rankings`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR (UUID) | PRIMARY KEY | Ranking ID |
| `user_id` | INTEGER | FOREIGN KEY (users.id), NOT NULL, INDEXED | Owner user ID |
| `job_id` | VARCHAR (UUID) | FOREIGN KEY (jobs.id), NOT NULL, INDEXED | Target job ID |
| `ranked_experience_ids` | JSON | NOT NULL, DEFAULT [] | Ranked experience UUIDs |
| `ranked_project_ids` | JSON | NOT NULL, DEFAULT [] | Ranked project UUIDs |
| `ranked_skill_ids` | JSON | NOT NULL, DEFAULT [] | Ranked skill UUIDs |
| `ranking_model_used` | VARCHAR | NULLABLE | Model used (e.g., llama-3.1-8b-instant) |
| `ranking_timestamp` | TIMESTAMP | DEFAULT NOW, NOT NULL | Ranking creation timestamp |
| `ranking_confidence_score` | FLOAT | NULLABLE | Confidence score (0.0-1.0) |
| `ranking_explanations` | JSON | DEFAULT {} | Explanations per item |
| `times_used_in_generation` | INTEGER | DEFAULT 0 | Usage counter |
| `last_used_at` | TIMESTAMP | NULLABLE | Last usage timestamp |
| `user_modified` | BOOLEAN | DEFAULT FALSE | User override flag |
| `user_override_timestamp` | TIMESTAMP | NULLABLE | User modification timestamp |
| `is_active` | BOOLEAN | DEFAULT TRUE, NOT NULL | Active status |
| `created_at` | TIMESTAMP | DEFAULT NOW, NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW, ON UPDATE NOW, NOT NULL | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id`
- INDEX on `job_id`

**Relationships**:
- MANY-TO-ONE with `users`
- MANY-TO-ONE with `jobs`

**JSON Field Structures**:

**ranked_experience_ids**:
```json
[
  "exp-uuid-1",  // Highest relevance
  "exp-uuid-3",
  "exp-uuid-2",
  "exp-uuid-5"
]
```

**ranking_explanations**:
```json
{
  "exp-uuid-1": {
    "relevance_score": 0.95,
    "reasoning": "Strong match with required Python and FastAPI skills, directly relevant AWS experience"
  },
  "exp-uuid-3": {
    "relevance_score": 0.82,
    "reasoning": "Demonstrates microservices architecture mentioned in job description"
  },
  "proj-uuid-2": {
    "relevance_score": 0.88,
    "reasoning": "Showcases real-world FastAPI implementation with similar tech stack"
  }
}
```

**Business Logic**:
- Rankings are cached per job for reuse across multiple generations
- LLM analyzes job requirements and ranks content by relevance
- Rankings can be overridden by users
- `times_used_in_generation` increments on each generation using this ranking

---

## Database Migrations

### Migration Tool: Alembic

**Configuration**: `backend/alembic.ini`

**Migrations Directory**: `backend/alembic/versions/`

### Common Migration Commands

**Create New Migration**:
```bash
cd backend
alembic revision --autogenerate -m "Add new column to table"
```

**Apply Migrations**:
```bash
alembic upgrade head
```

**Rollback Migration**:
```bash
alembic downgrade -1
```

**View Migration History**:
```bash
alembic history
```

**View Current Version**:
```bash
alembic current
```

---

## Indexes Summary

### Performance-Critical Indexes

1. **users**:
   - `email` (UNIQUE) - Login lookup

2. **master_profiles**:
   - `user_id` - Profile ownership queries

3. **experiences/education/projects**:
   - `profile_id` - Fetching profile content

4. **jobs**:
   - `user_id` - User's saved jobs
   - `source` - Job source filtering
   - `status` - Active/archived filtering
   - `application_status` - Application tracking
   - `created_at` - Recent jobs sorting

5. **generations**:
   - `user_id` - User's generation history
   - `profile_id` - Generations per profile
   - `job_id` - Generations for specific job
   - `status` - Active generations
   - `created_at` - Recent generations sorting

6. **sample_documents**:
   - `user_id` - User's samples
   - `document_type` - Filter by type

7. **job_content_rankings**:
   - `user_id` - User's rankings
   - `job_id` - Rankings for specific job (UNIQUE per user+job)

---

## Storage Estimates

### Typical Storage per User

| Data Type | Storage | Notes |
|-----------|---------|-------|
| User account | ~500 bytes | Minimal metadata |
| Master profile | ~2-5 KB | With 3-5 experiences, 2 education, 2 projects |
| 10 saved jobs | ~50 KB | Full job descriptions |
| 2 sample documents | ~10 KB | Text-only (.txt files) |
| 1 writing style | ~5 KB | JSON style analysis |
| 10 content rankings | ~20 KB | Ranked UUIDs with explanations |
| 20 generations | ~100 KB | Generated documents with metadata |

**Total per Active User**: ~185-200 KB
**1,000 Users**: ~200 MB
**10,000 Users**: ~2 GB

**Database Growth**: Moderate - primarily from generations (documents stored as text)

---

## Data Retention Policies

### Automatic Cleanup

1. **Expired Generations**:
   - Generations older than 90 days with status `completed`
   - Keep only latest 50 generations per user

2. **Archived Sample Documents**:
   - Soft delete via `is_active=false`
   - Hard delete after 30 days of archiving

3. **Old Content Rankings**:
   - Keep rankings for active jobs
   - Delete rankings when job is deleted (cascade)

### User Data Deletion

On user account deletion:
- CASCADE DELETE on all related tables
- Soft delete user with `is_active=false` for 30 days
- Hard delete after 30-day grace period

---

## Security Considerations

### Sensitive Data

1. **Password Storage**:
   - Bcrypt hashing with cost factor 12
   - Never store plain text passwords
   - Password hash stored in `users.password_hash`

2. **Personal Information**:
   - Email, phone, location in `personal_info` JSON
   - No SSN, payment info, or other PII stored

3. **Access Control**:
   - Row-level security via `user_id` foreign keys
   - All queries filtered by authenticated user
   - No cross-user data access

### Database Security

1. **Production**:
   - Encrypted connections (SSL/TLS)
   - Principle of least privilege for database users
   - Regular backups with encryption
   - Database-level encryption at rest

2. **Development**:
   - Local SQLite file
   - No sensitive production data in development

---

## Query Optimization Examples

### Fetch User Profile with All Content

```python
async def get_full_profile(db: AsyncSession, profile_id: str):
    """Fetch profile with all relationships in single query."""
    stmt = (
        select(MasterProfileModel)
        .options(
            selectinload(MasterProfileModel.experiences),
            selectinload(MasterProfileModel.education),
            selectinload(MasterProfileModel.projects),
        )
        .where(MasterProfileModel.id == profile_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
```

### Fetch User's Recent Generations

```python
async def get_recent_generations(db: AsyncSession, user_id: int, limit: int = 20):
    """Fetch recent generations with job and profile info."""
    stmt = (
        select(GenerationModel)
        .options(
            selectinload(GenerationModel.job),
            selectinload(GenerationModel.profile),
        )
        .where(GenerationModel.user_id == user_id)
        .order_by(GenerationModel.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
```

---

## Future Schema Changes

### Planned for v3.1

1. **exports** table:
   - Track exported PDF/DOCX files
   - File metadata and download tracking

2. **templates** table:
   - Resume/cover letter templates
   - Template customization settings

3. **generation_feedback** table:
   - User ratings for generated documents
   - Improvement suggestions

4. **job_applications** table:
   - Track actual job applications
   - Application timeline and notes

---

**Schema Version**: 3.0
**Last Updated**: November 2025
**Total Tables**: 10 core tables
**Migration Status**: Up to date
**Documentation**: Complete
