# Database Schema - JobWise AI Generation System v3.0

**Version**: 3.0  
**Last Updated**: November 16, 2025  
**Status**: 🎯 **Ready for Implementation**

---

## Schema Overview

This document defines all database changes required for the redesigned generation system.

### New Tables
1. `sample_documents` - Store user's sample resume and cover letter
2. `job_content_rankings` - Store job-specific content rankings
3. `prompt_templates` - Store LLM prompts with version control

### Modified Tables
1. `master_profiles` - Add `enhanced_professional_summary` column
2. `experiences` - Add `enhanced_description` column
3. `projects` - Add `enhanced_description` column
4. `generations` - Add `user_custom_prompt` column

### Removed Tables
- `writing_style_configs` (replaced by `sample_documents`)
- `layout_configs` (no longer needed - job-specific ranking instead)
- `user_generation_profiles` (too complex, removed)
- `example_resumes` (consolidated into `sample_documents`)
- `consistency_scores` (removed)
- `job_type_overrides` (removed)

---

## Table Definitions

### 1. sample_documents

**Purpose**: Store user's uploaded sample documents (resume and cover letter) as plain text.

```sql
CREATE TABLE sample_documents (
    id TEXT PRIMARY KEY,  -- UUID
    user_id INTEGER NOT NULL,
    
    -- Document metadata
    document_type TEXT NOT NULL CHECK(document_type IN ('resume', 'cover_letter')),
    original_filename TEXT,  -- Optional: track source file name
    
    -- Text storage
    original_text TEXT NOT NULL,  -- Full verbatim text from uploaded .txt file
    word_count INTEGER,
    character_count INTEGER,
    
    -- Usage tracking
    is_active BOOLEAN DEFAULT TRUE,  -- Only one active per type per user
    last_used_for_generation DATETIME,
    generation_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_sample_documents_user_id ON sample_documents(user_id);
CREATE INDEX idx_sample_documents_user_type ON sample_documents(user_id, document_type);
CREATE INDEX idx_sample_documents_active ON sample_documents(user_id, document_type, is_active);
```

**Business Rules**:
- Each user can have multiple sample documents per type, but only ONE `is_active=TRUE` per type
- When uploading a new sample, set previous samples of same type to `is_active=FALSE`
- `original_text` must be stored for re-analysis capability

### 1.5. writing_styles

**Purpose**: Store extracted writing style analysis for each user (derived from cover letter samples).

```sql
CREATE TABLE writing_styles (
    id TEXT PRIMARY KEY,  -- UUID
    user_id INTEGER NOT NULL UNIQUE,  -- One style per user
    
    -- Writing style analysis
    extracted_style TEXT NOT NULL,  -- JSON: complete style analysis results
    
    -- Extraction metadata
    extraction_status TEXT DEFAULT 'pending' NOT NULL,  -- pending, completed, failed
    extraction_model TEXT,  -- Model/method used for extraction
    extraction_timestamp DATETIME,
    extraction_confidence FLOAT,  -- 0.0-1.0 confidence score
    
    -- Source tracking
    source_sample_id TEXT,  -- Foreign key to sample_documents
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (source_sample_id) REFERENCES sample_documents(id) ON DELETE SET NULL
);

-- Indexes
CREATE UNIQUE INDEX idx_writing_styles_user_id ON writing_styles(user_id);
CREATE INDEX idx_writing_styles_status ON writing_styles(extraction_status);
```

**Business Rules**:
- One writing style per user (enforced by UNIQUE constraint on user_id)
- Extracted automatically when user uploads their first cover letter
- Can be re-extracted if needed (updates all metadata fields)
- `extracted_style` contains JSON with style characteristics (tone, vocabulary, formality, etc.)
- `source_sample_id` tracks which cover letter sample was used for extraction
- **Prototype limitation**: Only accepts .txt files (plain text upload)
- Future enhancement: Add PDF/DOCX support with BLOB storage if needed

**Example Data**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "document_type": "cover_letter",
  "original_filename": "Huy_Ky_General_Cover_Letter.txt",
  "original_text": "Dear Hiring Manager,\n\nI am a software engineering student at Washington State University with a passion for building scalable web applications and AI-powered systems. Through my coursework and personal projects, I have developed strong skills in Python, React, and cloud technologies.\n\nI am particularly interested in this position because...",
  "word_count": 421,
  "character_count": 2847,
  "extracted_writing_style": "{\"vocabulary_level\": \"professional\", \"tone\": \"enthusiastic\", \"formality_level\": 7, \"sentence_structure\": \"varied\", \"active_voice_ratio\": 0.85, \"action_verbs\": [\"developed\", \"architected\", \"implemented\"], \"technical_terms\": [\"AI-powered\", \"scalable\", \"cloud technologies\"], \"storytelling_style\": \"achievement-focused\"}",
  "style_extraction_status": "completed",
  "style_extraction_model": "llama-3.1-8b-instant",
  "style_extraction_timestamp": "2025-11-16T10:32:00Z",
  "style_extraction_confidence": 0.92,
  "is_active": true,
  "last_used_for_generation": "2025-11-16T14:20:00Z",
  "generation_count": 3,
  "created_at": "2025-11-16T10:30:00Z",
  "updated_at": "2025-11-16T14:20:00Z"
}
```

---

### 2. job_content_rankings

**Purpose**: Store LLM-generated rankings of user's experiences and projects for specific jobs.

```sql
CREATE TABLE job_content_rankings (
    id TEXT PRIMARY KEY,  -- UUID
    user_id INTEGER NOT NULL,
    job_id TEXT NOT NULL,  -- Foreign key to jobs table
    
    -- Ranked content (ordered lists of UUIDs)
    ranked_experience_ids TEXT NOT NULL,  -- JSON array: ["exp-uuid-1", "exp-uuid-2", ...]
    ranked_project_ids TEXT NOT NULL,  -- JSON array: ["proj-uuid-1", "proj-uuid-2", ...]
    
    -- Ranking metadata
    ranking_rationale TEXT,  -- Why this order? (from LLM explanation)
    keyword_matches TEXT,  -- JSON: {"Python": 3, "AWS": 2, ...}
    relevance_scores TEXT,  -- JSON: {"exp-uuid-1": 0.95, "proj-uuid-2": 0.87, ...}
    
    -- LLM metadata
    llm_model TEXT,  -- e.g., "llama-3.1-8b-instant"
    llm_tokens_used INTEGER,
    llm_generation_time FLOAT,  -- seconds
    prompt_template_id TEXT,  -- Foreign key to prompt_templates
    user_custom_prompt TEXT,  -- User's optional custom prompt
    
    -- Status
    status TEXT DEFAULT 'completed',  -- pending, completed, failed
    error_message TEXT,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (prompt_template_id) REFERENCES prompt_templates(id)
);

-- Indexes
CREATE INDEX idx_job_content_rankings_user_job ON job_content_rankings(user_id, job_id);
CREATE INDEX idx_job_content_rankings_job_id ON job_content_rankings(job_id);
CREATE UNIQUE INDEX idx_job_content_rankings_unique ON job_content_rankings(user_id, job_id);
```

**Business Rules**:
- One ranking per user per job (UNIQUE constraint)
- Ranking can be regenerated (updates existing record)
- `ranked_experience_ids` and `ranked_project_ids` are JSON arrays of UUIDs in priority order
- First item in array = highest relevance to job

**Example Data**:
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "job_id": "job-uuid-123",
  "ranked_experience_ids": "[\"exp-uuid-3\", \"exp-uuid-1\", \"exp-uuid-2\"]",
  "ranked_project_ids": "[\"proj-uuid-5\", \"proj-uuid-1\", \"proj-uuid-3\"]",
  "ranking_rationale": "Prioritized VR research experience and Azure Cloud project due to job's focus on AI/ML and cloud technologies.",
  "keyword_matches": "{\"Python\": 3, \"AI\": 2, \"Cloud\": 2, \"Machine Learning\": 1}",
  "relevance_scores": "{\"exp-uuid-3\": 0.95, \"exp-uuid-1\": 0.82, \"proj-uuid-5\": 0.91}",
  "llm_model": "llama-3.1-8b-instant",
  "llm_tokens_used": 1850,
  "llm_generation_time": 2.3,
  "prompt_template_id": "template-ranking-v1",
  "user_custom_prompt": "Emphasize AI research experience",
  "status": "completed"
}
```

---

### 3. prompt_templates

**Purpose**: Store LLM prompts with version control for consistency and experimentation.

```sql
CREATE TABLE prompt_templates (
    id TEXT PRIMARY KEY,  -- UUID or semantic ID like "content-ranking-v1"
    
    -- Template metadata
    template_name TEXT NOT NULL UNIQUE,  -- e.g., "content_ranking", "profile_enhancement"
    template_version TEXT NOT NULL,  -- Semantic versioning: "1.0.0", "1.1.0", "2.0.0"
    description TEXT,
    
    -- Prompt content
    prompt_template TEXT NOT NULL,  -- Jinja2 template with {{ variables }}
    system_message TEXT,  -- Optional system message for LLM
    expected_output_format TEXT,  -- JSON, text, markdown
    
    -- Configuration
    default_temperature FLOAT DEFAULT 0.3,
    default_max_tokens INTEGER DEFAULT 2000,
    target_llm_model TEXT,  -- Recommended model: llama-3.1-8b-instant, llama-3.3-70b-versatile
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at DATETIME,
    success_rate FLOAT,  -- 0.0-1.0 (successful generations / total attempts)
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,  -- One default per template_name
    deprecated_at DATETIME,
    deprecated_reason TEXT,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_prompt_templates_name ON prompt_templates(template_name);
CREATE INDEX idx_prompt_templates_active ON prompt_templates(is_active, template_name);
CREATE UNIQUE INDEX idx_prompt_templates_default ON prompt_templates(template_name, is_default) WHERE is_default = TRUE;
```

**Business Rules**:
- One default template per `template_name`
- Templates use Jinja2 syntax for variable substitution
- Versions follow semantic versioning
- Old templates can be deprecated but not deleted (audit trail)

**Example Data**:
```json
{
  "id": "template-ranking-v1",
  "template_name": "content_ranking",
  "template_version": "1.0.0",
  "description": "Rank user's experiences and projects by relevance to job posting",
  "prompt_template": "You are an expert career advisor...\n\nJob Description:\n{{ job_description }}\n\nUser Experiences:\n{{ experiences }}\n\nUser Projects:\n{{ projects }}\n\n{{ user_custom_prompt }}\n\nRank the experiences and projects...",
  "system_message": "You are a professional resume optimizer with expertise in ATS systems.",
  "expected_output_format": "JSON",
  "default_temperature": 0.3,
  "default_max_tokens": 2000,
  "target_llm_model": "llama-3.1-8b-instant",
  "is_active": true,
  "is_default": true
}
```

---

### 4. Enhanced Columns - master_profiles

**Purpose**: Store AI-enhanced version of professional summary.

```sql
ALTER TABLE master_profiles 
ADD COLUMN enhanced_professional_summary TEXT;

ALTER TABLE master_profiles 
ADD COLUMN enhancement_metadata TEXT;  -- JSON: {llm_model, tokens_used, enhanced_at, writing_style_source}
```

**Business Rules**:
- `professional_summary` = original user-written text (never modified)
- `enhanced_professional_summary` = AI-polished version using writing style from sample cover letter
- `enhancement_metadata` tracks which LLM and settings were used

**Example**:
```json
{
  "professional_summary": "Computer science student with experience in AI and cloud computing.",
  "enhanced_professional_summary": "First-generation computer science student with a 4.0 GPA pursuing a B.S. in Software Engineering. Experienced in AI orchestration, full-stack development, and system architecture with a strong foundation in algorithms, data structures, and cross-platform development. Passionate about building scalable solutions and mentoring peers, seeking opportunities to apply technical expertise and collaborative skills in software engineering and systems design.",
  "enhancement_metadata": "{\"llm_model\": \"llama-3.3-70b-versatile\", \"tokens_used\": 450, \"enhanced_at\": \"2025-11-16T11:00:00Z\", \"writing_style_source\": \"sample-doc-uuid\"}"
}
```

---

### 5. Enhanced Columns - experiences

**Purpose**: Store AI-enhanced version of experience descriptions.

```sql
ALTER TABLE experiences 
ADD COLUMN enhanced_description TEXT;

ALTER TABLE experiences 
ADD COLUMN enhancement_metadata TEXT;  -- JSON: {llm_model, tokens_used, enhanced_at}
```

**Business Rules**:
- `description` = original user-written text (never modified)
- `enhanced_description` = AI-polished version using writing style
- Enhancement preserves factual content, only improves clarity and style

**Example**:
```json
{
  "description": "Helped students with programming and math.",
  "enhanced_description": "Assist students with technical challenges across programming languages and mathematical concepts, providing individualized support to enhance problem-solving skills. Break down complex algorithms and software design principles into clear, digestible explanations to strengthen student understanding and confidence. Adapt tutoring approaches to meet diverse learning styles and skill levels, fostering inclusive and effective learning environments.",
  "enhancement_metadata": "{\"llm_model\": \"llama-3.3-70b-versatile\", \"tokens_used\": 320}"
}
```

---

### 6. Enhanced Columns - projects

**Purpose**: Store AI-enhanced version of project descriptions.

```sql
ALTER TABLE projects 
ADD COLUMN enhanced_description TEXT;

ALTER TABLE projects 
ADD COLUMN enhancement_metadata TEXT;  -- JSON: {llm_model, tokens_used, enhanced_at}
```

**Business Rules**:
- Same as experiences table
- Enhancement focuses on impact and technical depth

**Example**:
```json
{
  "description": "Built a recipe finder app that suggests recipes from ingredients.",
  "enhanced_description": "Architected a high-performance desktop application that generates a sorted graph of recipes from a given list of ingredients, completing the project within a 24-hour hackathon timeframe. Implemented MVVM design pattern to separate business logic from UI, ensuring maintainable and testable code structure. Designed efficient graph algorithms to optimize recipe suggestion logic based on ingredient availability and user preferences.",
  "enhancement_metadata": "{\"llm_model\": \"llama-3.3-70b-versatile\", \"tokens_used\": 380}"
}
```

---

### 7. Modified - generations

**Purpose**: Add support for user custom prompts.

```sql
ALTER TABLE generations 
ADD COLUMN user_custom_prompt TEXT;  -- User's optional prompt addition

ALTER TABLE generations 
ADD COLUMN prompt_template_id TEXT;  -- Which prompt template was used

ALTER TABLE generations
ADD FOREIGN KEY (prompt_template_id) REFERENCES prompt_templates(id);
```

**Business Rules**:
- `user_custom_prompt` is appended to base prompt template
- If NULL, only base template is used
- `prompt_template_id` links to template for audit trail

---

## Migration Scripts

### Migration 1: Create sample_documents table

```python
# backend/migrations/add_sample_documents_table.py
import sqlite3

def upgrade():
    conn = sqlite3.connect('jobwise.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sample_documents (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            document_type TEXT NOT NULL CHECK(document_type IN ('resume', 'cover_letter')),
            original_filename TEXT,
            original_text TEXT NOT NULL,
            word_count INTEGER,
            character_count INTEGER,
            is_active BOOLEAN DEFAULT TRUE,
            last_used_for_generation DATETIME,
            generation_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX idx_sample_documents_user_id ON sample_documents(user_id)")
    cursor.execute("CREATE INDEX idx_sample_documents_user_type ON sample_documents(user_id, document_type)")
    cursor.execute("CREATE INDEX idx_sample_documents_active ON sample_documents(user_id, document_type, is_active)")
    
    conn.commit()
    conn.close()
    print("✅ Created sample_documents table")

def downgrade():
    conn = sqlite3.connect('jobwise.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS sample_documents")
    conn.commit()
    conn.close()
    print("✅ Dropped sample_documents table")

if __name__ == "__main__":
    upgrade()
```

### Migration 2: Create job_content_rankings table

```python
# backend/migrations/add_job_content_rankings_table.py
import sqlite3

def upgrade():
    conn = sqlite3.connect('jobwise.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_content_rankings (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            job_id TEXT NOT NULL,
            ranked_experience_ids TEXT NOT NULL,
            ranked_project_ids TEXT NOT NULL,
            ranking_rationale TEXT,
            keyword_matches TEXT,
            relevance_scores TEXT,
            llm_model TEXT,
            llm_tokens_used INTEGER,
            llm_generation_time FLOAT,
            prompt_template_id TEXT,
            user_custom_prompt TEXT,
            status TEXT DEFAULT 'completed',
            error_message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
            FOREIGN KEY (prompt_template_id) REFERENCES prompt_templates(id)
        )
    """)
    
    cursor.execute("CREATE INDEX idx_job_content_rankings_user_job ON job_content_rankings(user_id, job_id)")
    cursor.execute("CREATE INDEX idx_job_content_rankings_job_id ON job_content_rankings(job_id)")
    cursor.execute("CREATE UNIQUE INDEX idx_job_content_rankings_unique ON job_content_rankings(user_id, job_id)")
    
    conn.commit()
    conn.close()
    print("✅ Created job_content_rankings table")

if __name__ == "__main__":
    upgrade()
```

### Migration 3: Create prompt_templates table

```python
# backend/migrations/add_prompt_templates_table.py
import sqlite3

def upgrade():
    conn = sqlite3.connect('jobwise.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prompt_templates (
            id TEXT PRIMARY KEY,
            template_name TEXT NOT NULL UNIQUE,
            template_version TEXT NOT NULL,
            description TEXT,
            prompt_template TEXT NOT NULL,
            system_message TEXT,
            expected_output_format TEXT,
            default_temperature FLOAT DEFAULT 0.3,
            default_max_tokens INTEGER DEFAULT 2000,
            target_llm_model TEXT,
            usage_count INTEGER DEFAULT 0,
            last_used_at DATETIME,
            success_rate FLOAT,
            is_active BOOLEAN DEFAULT TRUE,
            is_default BOOLEAN DEFAULT FALSE,
            deprecated_at DATETIME,
            deprecated_reason TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("CREATE INDEX idx_prompt_templates_name ON prompt_templates(template_name)")
    cursor.execute("CREATE INDEX idx_prompt_templates_active ON prompt_templates(is_active, template_name)")
    
    conn.commit()
    conn.close()
    print("✅ Created prompt_templates table")

if __name__ == "__main__":
    upgrade()
```

### Migration 4: Add enhanced columns

```python
# backend/migrations/add_enhanced_description_columns.py
import sqlite3

def upgrade():
    conn = sqlite3.connect('jobwise.db')
    cursor = conn.cursor()
    
    # Add to master_profiles
    cursor.execute("ALTER TABLE master_profiles ADD COLUMN enhanced_professional_summary TEXT")
    cursor.execute("ALTER TABLE master_profiles ADD COLUMN enhancement_metadata TEXT")
    
    # Add to experiences
    cursor.execute("ALTER TABLE experiences ADD COLUMN enhanced_description TEXT")
    cursor.execute("ALTER TABLE experiences ADD COLUMN enhancement_metadata TEXT")
    
    # Add to projects
    cursor.execute("ALTER TABLE projects ADD COLUMN enhanced_description TEXT")
    cursor.execute("ALTER TABLE projects ADD COLUMN enhancement_metadata TEXT")
    
    # Add to generations
    cursor.execute("ALTER TABLE generations ADD COLUMN user_custom_prompt TEXT")
    cursor.execute("ALTER TABLE generations ADD COLUMN prompt_template_id TEXT")
    
    conn.commit()
    conn.close()
    print("✅ Added enhanced description columns")

if __name__ == "__main__":
    upgrade()
```

---

## Data Flow Examples

### Example 1: User Uploads Sample Cover Letter

```python
# Request: POST /samples/upload-cover-letter
{
  "file": <uploaded_file>
}

# Database INSERT
INSERT INTO sample_documents (
  id, user_id, document_type, file_name, file_size, file_mime_type,
  file_path, original_text, word_count, character_count,
  extraction_method, is_active
) VALUES (
  'uuid-123', 1, 'cover_letter', 'my_cover_letter.txt', 2847,
  'text/plain', 'uploads/samples/user_1/cover_letter_uuid-123.txt',
  'Dear Hiring Manager...', 421, 2847, 'txt_direct', TRUE
);

# Deactivate previous cover letters
UPDATE sample_documents 
SET is_active = FALSE 
WHERE user_id = 1 AND document_type = 'cover_letter' AND id != 'uuid-123';
```

### Example 2: Enhance Profile Descriptions

```python
# Request: POST /profile/enhance
{
  "profile_id": "profile-uuid-456"
}

# Step 1: Fetch sample cover letter
SELECT original_text FROM sample_documents 
WHERE user_id = 1 AND document_type = 'cover_letter' AND is_active = TRUE;

# Step 2: LLM extracts writing style (in-memory, not stored)

# Step 3: Enhance professional summary
UPDATE master_profiles 
SET 
  enhanced_professional_summary = 'First-generation computer science student...',
  enhancement_metadata = '{"llm_model": "llama-3.3-70b-versatile", ...}'
WHERE id = 'profile-uuid-456';

# Step 4: Enhance each experience
UPDATE experiences 
SET 
  enhanced_description = 'Architected an AI-powered Sommelier NPC...',
  enhancement_metadata = '{"llm_model": "llama-3.3-70b-versatile", ...}'
WHERE profile_id = 'profile-uuid-456';

# Step 5: Enhance each project
UPDATE projects 
SET 
  enhanced_description = 'Built a fully functional desktop spreadsheet...',
  enhancement_metadata = '{"llm_model": "llama-3.3-70b-versatile", ...}'
WHERE profile_id = 'profile-uuid-456';
```

### Example 3: Rank Content for Job

```python
# Request: POST /rankings/create
{
  "job_id": "job-uuid-789",
  "custom_prompt": "Emphasize leadership and cloud experience"
}

# Database INSERT (or UPDATE if exists)
INSERT INTO job_content_rankings (
  id, user_id, job_id, ranked_experience_ids, ranked_project_ids,
  ranking_rationale, llm_model, user_custom_prompt
) VALUES (
  'ranking-uuid-999', 1, 'job-uuid-789',
  '["exp-3", "exp-1", "exp-2"]',
  '["proj-5", "proj-1", "proj-3"]',
  'Prioritized VR research and Azure project...',
  'llama-3.1-8b-instant',
  'Emphasize leadership and cloud experience'
)
ON CONFLICT(user_id, job_id) DO UPDATE SET
  ranked_experience_ids = excluded.ranked_experience_ids,
  ranked_project_ids = excluded.ranked_project_ids,
  updated_at = CURRENT_TIMESTAMP;
```

---

## Storage Estimates

### For 1000 Users

| Table | Avg Rows/User | Row Size | Total Size |
|-------|---------------|----------|------------|
| `sample_documents` | 2 (resume + cover letter) | ~5 KB | 10 MB |
| `job_content_rankings` | 10 (10 jobs applied to) | ~2 KB | 20 MB |
| `prompt_templates` | N/A (shared) | ~3 KB | 0.1 MB |
| Enhanced columns | 1 profile + 5 exp + 5 proj | ~500 B each | 5.5 MB |
| **Total Additional Storage** | | | **~36 MB** |

**Conclusion**: Negligible storage overhead. Full text storage is feasible.

---

## Next Steps

1. Review this schema for completeness
2. Approve or request modifications
3. Run migration scripts in development
4. Seed default prompt templates
5. Proceed to [02-AI-PIPELINE.md](02-AI-PIPELINE.md)
