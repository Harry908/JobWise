# Profile API

**Version**: 1.0

**At a Glance**
- **Service Name**: Profile Management
- **Primary Tables**: `master_profiles`, `experiences`, `education`, `projects`
- **Key Dependencies**: `users` (ownership), AI enhancement models (v3)
- **Auth Required**: Yes (Bearer JWT)
- **Primary Routes**: `/profiles`, `/profiles/{profile_id}`, `/profiles/{profile_id}/experiences`, `/profiles/{profile_id}/analytics`

**Related Docs**
- Backend Architecture: `../BACKEND_ARCHITECTURE_OVERVIEW.md`
- Database Schema: `06-database-schema.md`
- Jobs API: `03-job-api.md`
- Generation API: `04b-ai-generation-api.md`
- Mobile Feature: `../mobile-new/02-profile-management-feature.md`

**Key Field Semantics**
- `profile_id`: UUID primary key of `master_profiles`; required on all profile-scoped endpoints.
- `user_id`: Owner of the profile; derived from the authenticated user and never taken from the client.
- `personal_info`: JSON object with contact details, links, etc.
- `skills`: JSON grouping of technical, soft, languages, and certifications.
- `enhanced_*` fields: AI-enhanced copies of summaries/descriptions; original fields remain as user-authored content.
**Base Path**: `/api/v1/profiles`
**Status**: ✅ Fully Implemented

---

## Overview

The Profile API manages user master resume profiles, including personal information, experiences, education, projects, skills, and custom fields. This serves as the central repository of user career data used for AI-powered document generation.

**Key Features**:
- Complete CRUD operations for profiles
- Bulk operations for experiences, education, and projects
- Skills management (technical, soft, languages, certifications)
- Custom fields support for flexibility
- Profile completeness analytics
- Multi-profile support per user

---

## Profile Structure

```
Profile
├── Personal Info (name, email, phone, location, links)
├── Professional Summary (text summary of career)
├── Enhanced Summary (AI-generated improvement)
├── Skills
│   ├── Technical Skills (e.g., Python, React, AWS)
│   ├── Soft Skills (e.g., Leadership, Communication)
│   ├── Languages (name + proficiency level)
│   └── Certifications (name, issuer, dates, credentials)
├── Experiences (work history)
│   ├── Title, Company, Location
│   ├── Dates (start, end, is_current)
│   ├── Description (original user-authored, max 2000 chars)
│   ├── Enhanced Description (AI-generated, max 2000 chars, optional)
│   └── Achievements (list of accomplishments)
├── Education
│   ├── Institution, Degree, Field of Study
│   ├── Dates, GPA
│   └── Honors
├── Projects
│   ├── Name, Description (original, max 1000 chars)
│   ├── Enhanced Description (AI-generated, max 1000 chars, optional)
│   ├── Technologies, URLs
│   └── Dates
└── Custom Fields (flexible key-value pairs)
```

---

## Endpoints Summary

### Profile CRUD
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create new profile |
| GET | `/` | List all user's profiles |
| GET | `/me` | Get user's primary profile |
| GET | `/{profile_id}` | Get specific profile |
| PUT | `/{profile_id}` | Update profile |
| DELETE | `/{profile_id}` | Delete profile |

### Profile Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{profile_id}/analytics` | Get profile completeness score |

### Experiences
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/{profile_id}/experiences` | Add experiences (single or bulk) |
| GET | `/{profile_id}/experiences` | Get all experiences |
| PUT | `/{profile_id}/experiences` | Update experiences (single or bulk) |
| DELETE | `/{profile_id}/experiences` | Delete experiences (single or bulk) |

### Education
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/{profile_id}/education` | Add education entries (single or bulk) |
| PUT | `/{profile_id}/education` | Update education entries |
| DELETE | `/{profile_id}/education` | Delete education entries |

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/{profile_id}/projects` | Add projects (single or bulk) |
| PUT | `/{profile_id}/projects` | Update projects |
| DELETE | `/{profile_id}/projects` | Delete projects |

### Skills
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{profile_id}/skills` | Get all skills |
| PUT | `/{profile_id}/skills` | Update all skills |
| POST | `/{profile_id}/skills/technical` | Add technical skills |
| DELETE | `/{profile_id}/skills/technical` | Remove technical skills |
| POST | `/{profile_id}/skills/soft` | Add soft skills |
| DELETE | `/{profile_id}/skills/soft` | Remove soft skills |

### Custom Fields
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{profile_id}/custom-fields` | Get custom fields |
| POST | `/{profile_id}/custom-fields` | Add custom fields |
| PUT | `/{profile_id}/custom-fields` | Update custom fields |

**Total Endpoints**: 24

---

## Core Profile Endpoints

### 1. Create Profile

Create a new master resume profile.

**Endpoint**: `POST /api/v1/profiles`

**Authentication**: Required

**Request Body**:
```json
{
  "personal_info": {
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-123-4567",
    "location": "Seattle, WA",
    "linkedin": "https://linkedin.com/in/johndoe",
    "github": "https://github.com/johndoe",
    "website": "https://johndoe.com"
  },
  "professional_summary": "Senior Software Engineer with 8+ years of experience...",
  "skills": {
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
  },
  "custom_fields": {
    "portfolio_url": "https://portfolio.johndoe.com",
    "preferred_location": "Remote, USA"
  }
}
```

**Success Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "personal_info": {
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-123-4567",
    "location": "Seattle, WA",
    "linkedin": "https://linkedin.com/in/johndoe",
    "github": "https://github.com/johndoe",
    "website": "https://johndoe.com"
  },
  "professional_summary": "Senior Software Engineer with 8+ years...",
  "enhanced_summary": null,
  "skills": {
    "technical": ["Python", "FastAPI", "React", "AWS"],
    "soft": ["Leadership", "Communication", "Problem Solving"],
    "languages": [
      {"name": "English", "proficiency": "native"}
    ],
    "certifications": [...]
  },
  "custom_fields": {...},
  "is_primary": true,
  "created_at": "2025-11-15T10:30:00Z",
  "updated_at": "2025-11-15T10:30:00Z"
}
```

---

### 2. Get User's Primary Profile

Retrieve the user's primary (default) profile.

**Endpoint**: `GET /api/v1/profiles/me`

**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "personal_info": {...},
  "professional_summary": "...",
  "enhanced_summary": null,
  "skills": {...},
  "experiences": [
    {
      "id": "exp_123",
      "title": "Senior Software Engineer",
      "company": "Tech Corp",
      "location": "Seattle, WA",
      "start_date": "2020-01-01",
      "end_date": "2023-12-31",
      "is_current": false,
      "description": "Led development of scalable web applications",
      "enhanced_description": null,
      "achievements": ["Increased performance by 40%"]
    }
  ],
  "education": [...],
  "projects": [...],
  "custom_fields": {...},
  "is_primary": true,
  "created_at": "2025-11-15T10:30:00Z",
  "updated_at": "2025-11-15T10:30:00Z"
}
```

**Error Responses**:

**404 Not Found**:
```json
{
  "detail": "No profile found for this user"
}
```

---

### 3. Get Specific Profile

Retrieve a profile by ID.

**Endpoint**: `GET /api/v1/profiles/{profile_id}`

**Authentication**: Required

**Path Parameters**:
- `profile_id` (UUID): Profile unique identifier

**Success Response** (200 OK): Same as "Get User's Primary Profile"

**Error Responses**:

**404 Not Found**:
```json
{
  "detail": "Profile not found"
}
```

**403 Forbidden**:
```json
{
  "detail": "You do not have permission to access this profile"
}
```

---

### 4. Update Profile

Update profile information (partial updates supported).

**Endpoint**: `PUT /api/v1/profiles/{profile_id}`

**Authentication**: Required

**Request Body** (all fields optional):
```json
{
  "personal_info": {
    "full_name": "John Doe Jr.",
    "phone": "+1-555-999-8888"
  },
  "professional_summary": "Updated professional summary..."
}
```

**Success Response** (200 OK): Full updated profile

---

### 5. Delete Profile

Delete a profile permanently.

**Endpoint**: `DELETE /api/v1/profiles/{profile_id}`

**Authentication**: Required

**Success Response** (204 No Content): No body

**Error Responses**:

**403 Forbidden** (Cannot delete primary profile):
```json
{
  "detail": "Cannot delete primary profile. Create another profile first."
}
```

---

### 6. Get Profile Analytics

Get profile completeness score and recommendations.

**Endpoint**: `GET /api/v1/profiles/{profile_id}/analytics`

**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "completeness_score": 85,
  "missing_sections": ["certifications"],
  "recommendations": [
    "Add at least 2 professional certifications",
    "Enhance your professional summary with AI"
  ],
  "strengths": [
    "Strong technical skills portfolio",
    "Comprehensive work experience",
    "Multiple projects showcased"
  ],
  "stats": {
    "total_experiences": 4,
    "total_education": 2,
    "total_projects": 6,
    "total_technical_skills": 15,
    "total_soft_skills": 5
  }
}
```

---

## Experience Endpoints

### 7. Add Experiences (Bulk)

Add one or more experiences to profile.

**Endpoint**: `POST /api/v1/profiles/{profile_id}/experiences`

**Authentication**: Required

**Request Body (Single)**:
```json
{
  "title": "Senior Software Engineer",
  "company": "Tech Corp",
  "location": "Seattle, WA",
  "start_date": "2020-01-01",
  "end_date": "2023-12-31",
  "is_current": false,
  "description": "Led development of scalable microservices\nImplemented CI/CD pipelines\nMentored junior developers",
  "achievements": [
    "Increased API performance by 40%",
    "Reduced deployment time from 2 hours to 15 minutes"
  ],
  "technologies": ["Python", "FastAPI", "Docker", "AWS"]
}
```

**Note**: Do NOT include an `id` field in the request. IDs are automatically generated by the backend.

**Request Body (Bulk)**:
```json
{
  "experiences": [
    {...},
    {...},
    {...}
  ]
}
```

**Success Response** (201 Created):
```json
{
  "message": "3 experiences added successfully",
  "ids": ["exp_123", "exp_456", "exp_789"]
}
```

---

### 8. Get All Experiences

Retrieve all experiences for a profile.

**Endpoint**: `GET /api/v1/profiles/{profile_id}/experiences`

**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "experiences": [
    {
      "id": "exp_123",
      "title": "Senior Software Engineer",
      "company": "Tech Corp",
      "location": "Seattle, WA",
      "start_date": "2020-01-01",
      "end_date": "2023-12-31",
      "is_current": false,
      "description": "Led development...",
      "enhanced_description": "Spearheaded the development...",
      "achievements": ["..."]
    }
  ],
  "total": 4
}
```

---

### 9. Update Experiences (Bulk)

Update one or more experiences.

**Endpoint**: `PUT /api/v1/profiles/{profile_id}/experiences`

**Authentication**: Required

**Request Body (Single)**:
```json
{
  "id": "exp_123",
  "title": "Lead Software Engineer",
  "is_current": true,
  "end_date": null
}
```

**Request Body (Bulk)**:
```json
{
  "experiences": [
    {"id": "exp_123", "title": "Lead Software Engineer"},
    {"id": "exp_456", "location": "Remote"}
  ]
}
```

**Success Response** (200 OK):
```json
{
  "message": "2 experiences updated successfully"
}
```

---

### 10. Delete Experiences (Bulk)

Delete one or more experiences.

**Endpoint**: `DELETE /api/v1/profiles/{profile_id}/experiences`

**Authentication**: Required

**Request Body (Single)**:
```json
{
  "id": "exp_123"
}
```

**Request Body (Bulk)**:
```json
{
  "ids": ["exp_123", "exp_456", "exp_789"]
}
```

**Success Response** (204 No Content): No body

---

## Education Endpoints

### 11. Add Education (Bulk)

Add one or more education entries.

**Endpoint**: `POST /api/v1/profiles/{profile_id}/education`

**Authentication**: Required

**Request Body**:
```json
{
  "institution": "University of Washington",
  "degree": "Bachelor of Science",
  "field_of_study": "Computer Science",
  "start_date": "2016-09-01",
  "end_date": "2020-06-15",
  "gpa": 3.85,
  "honors": [
    "Summa Cum Laude",
    "Dean's List (8 quarters)"
  ],
  "relevant_coursework": [
    "Data Structures",
    "Algorithms",
    "Machine Learning"
  ]
}
```

**Note**: Do NOT include an `id` field in the request. IDs are automatically generated by the backend.

**Success Response** (201 Created):
```json
{
  "message": "Education added successfully",
  "id": "edu_123"
}
```

---

### 12. Update Education (Bulk)

Update education entries.

**Endpoint**: `PUT /api/v1/profiles/{profile_id}/education`

**Authentication**: Required

**Request Body**: Similar to Add Education (include `id` field)

---

### 13. Delete Education (Bulk)

Delete education entries.

**Endpoint**: `DELETE /api/v1/profiles/{profile_id}/education`

**Authentication**: Required

**Request Body**:
```json
{
  "education_ids": ["edu_123", "edu_456"]
}
```

**Success Response** (200 OK):
```json
{
  "message": "Deleted 2 education entries successfully"
}
```

---

## Project Endpoints

### 14. Add Projects (Bulk)

Add one or more projects.

**Endpoint**: `POST /api/v1/profiles/{profile_id}/projects`

**Authentication**: Required

**Request Body**:
```json
{
  "name": "JobWise - AI Resume Generator",
  "description": "AI-powered platform for generating tailored resumes and cover letters\nBuilt with FastAPI backend and Flutter mobile app\nIntegrated Groq LLM for content generation",
  "technologies": ["Python", "FastAPI", "Flutter", "Groq LLM", "SQLAlchemy"],
  "url": "https://jobwise.app",
  "github_url": "https://github.com/johndoe/jobwise",
  "start_date": "2024-06-01",
  "end_date": "2025-11-01"
}
```

**Note**: Do NOT include an `id` field in the request. IDs are automatically generated by the backend.

**Success Response** (201 Created):
```json
{
  "message": "Project added successfully",
  "id": "proj_123"
}
```

---

### 15. Update Projects (Bulk)

Update projects.

**Endpoint**: `PUT /api/v1/profiles/{profile_id}/projects`

**Authentication**: Required

**Request Body**: Similar to Add Projects (include `id` field)

---

### 16. Delete Projects (Bulk)

Delete projects.

**Endpoint**: `DELETE /api/v1/profiles/{profile_id}/projects`

**Authentication**: Required

**Request Body**:
```json
{
  "project_ids": ["proj_123", "proj_456"]
}
```

**Success Response** (200 OK):
```json
{
  "message": "Deleted 2 projects successfully"
}
```

---

## Skills Endpoints

### 17. Get All Skills

Retrieve all skills for a profile.

**Endpoint**: `GET /api/v1/profiles/{profile_id}/skills`

**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "technical": [
    "Python", "JavaScript", "FastAPI", "React",
    "Docker", "AWS", "PostgreSQL", "Git"
  ],
  "soft": [
    "Leadership", "Communication", "Problem Solving",
    "Team Collaboration", "Agile Methodologies"
  ],
  "languages": [
    {"name": "English", "proficiency": "native"},
    {"name": "Spanish", "proficiency": "conversational"}
  ],
  "certifications": [
    {
      "name": "AWS Solutions Architect Associate",
      "issuer": "Amazon Web Services",
      "date_obtained": "2023-01-15",
      "expiry_date": "2026-01-15",
      "credential_id": "AWS-SAA-123456"
    }
  ]
}
```

---

### 18. Update All Skills

Replace all skills (bulk update).

**Endpoint**: `PUT /api/v1/profiles/{profile_id}/skills`

**Authentication**: Required

**Request Body**: Same as Get All Skills response

---

### 19. Add Technical Skills

Add technical skills to existing list.

**Endpoint**: `POST /api/v1/profiles/{profile_id}/skills/technical`

**Authentication**: Required

**Request Body**:
```json
{
  "skills": ["Kubernetes", "GraphQL", "Redis"]
}
```

**Success Response** (200 OK):
```json
{
  "message": "3 technical skills added",
  "technical_skills": [
    "Python", "JavaScript", "FastAPI", "React",
    "Kubernetes", "GraphQL", "Redis"
  ]
}
```

---

### 20. Remove Technical Skills

Remove technical skills from list.

**Endpoint**: `DELETE /api/v1/profiles/{profile_id}/skills/technical`

**Authentication**: Required

**Request Body**:
```json
{
  "skills": ["Redis", "GraphQL"]
}
```

**Success Response** (200 OK):
```json
{
  "message": "2 technical skills removed",
  "technical_skills": ["Python", "JavaScript", "FastAPI", "React", "Kubernetes"]
}
```

---

### 21. Add Soft Skills

Add soft skills to existing list.

**Endpoint**: `POST /api/v1/profiles/{profile_id}/skills/soft`

**Authentication**: Required

**Request Body**:
```json
{
  "skills": ["Critical Thinking", "Mentorship"]
}
```

---

### 22. Remove Soft Skills

Remove soft skills from list.

**Endpoint**: `DELETE /api/v1/profiles/{profile_id}/skills/soft`

**Authentication**: Required

**Request Body**:
```json
{
  "skills": ["Critical Thinking"]
}
```

---

## Custom Fields Endpoints

### 23. Get Custom Fields

Retrieve all custom fields for a profile.

**Endpoint**: `GET /api/v1/profiles/{profile_id}/custom-fields`

**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "custom_fields": {
    "portfolio_url": "https://portfolio.johndoe.com",
    "preferred_location": "Remote, USA",
    "salary_expectations": "$120k-$150k",
    "security_clearance": "Secret",
    "availability": "2 weeks notice"
  }
}
```

---

### 24. Add Custom Fields

Add new custom fields.

**Endpoint**: `POST /api/v1/profiles/{profile_id}/custom-fields`

**Authentication**: Required

**Request Body**:
```json
{
  "fields": {
    "linkedin_profile": "https://linkedin.com/in/johndoe",
    "preferred_industries": "Tech, Finance, Healthcare"
  }
}
```

**Success Response** (201 Created):
```json
{
  "message": "2 custom fields added",
  "custom_fields": {...all fields...}
}
```

---

### 25. Update Custom Fields

Update existing custom fields.

**Endpoint**: `PUT /api/v1/profiles/{profile_id}/custom-fields`

**Authentication**: Required

**Request Body**:
```json
{
  "fields": {
    "salary_expectations": "$130k-$160k",
    "availability": "Immediate"
  }
}
```

---

## Database Schema

### master_profiles Table

```sql
CREATE TABLE master_profiles (
    id VARCHAR PRIMARY KEY,  -- UUID
    user_id INTEGER NOT NULL,
    personal_info TEXT NOT NULL,  -- JSON
    professional_summary TEXT,
    enhanced_summary TEXT,
    skills TEXT,  -- JSON
    custom_fields TEXT,  -- JSON
    is_primary BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_master_profiles_user_id ON master_profiles(user_id);
```

### experiences Table

```sql
CREATE TABLE experiences (
    id VARCHAR PRIMARY KEY,  -- UUID
    profile_id VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    company VARCHAR NOT NULL,
    location VARCHAR,
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    description TEXT,
    enhanced_description TEXT,
    achievements TEXT,  -- JSON array
    technologies TEXT,  -- JSON array
    display_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES master_profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_experiences_profile_id ON experiences(profile_id);
```

### education Table

```sql
CREATE TABLE education (
    id VARCHAR PRIMARY KEY,
    profile_id VARCHAR NOT NULL,
    institution VARCHAR NOT NULL,
    degree VARCHAR NOT NULL,
    field_of_study VARCHAR,
    start_date DATE,
    end_date DATE,
    gpa REAL,
    honors TEXT,  -- JSON array
    relevant_coursework TEXT,  -- JSON array
    display_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES master_profiles(id) ON DELETE CASCADE
);
```

### projects Table

```sql
CREATE TABLE projects (
    id VARCHAR PRIMARY KEY,
    profile_id VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    description TEXT,
    enhanced_description TEXT,
    technologies TEXT,  -- JSON array
    url VARCHAR,
    github_url VARCHAR,
    start_date DATE,
    end_date DATE,
    display_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES master_profiles(id) ON DELETE CASCADE
);
```

---

## Best Practices

### 1. ID Management
**Never include `id` fields in POST requests** - IDs are automatically generated:
- Experience IDs: UUIDs auto-generated by the backend
- Education IDs: UUIDs auto-generated by the backend
- Project IDs: UUIDs auto-generated by the backend
- Profile IDs: UUIDs auto-generated by the backend

**Only include `id` fields in PUT/DELETE requests** to identify existing items.

### 2. Profile Completeness
For best AI generation results, ensure profiles have:
- ✅ Complete personal info (name, email, location)
- ✅ Professional summary (2-3 sentences)
- ✅ At least 3 work experiences
- ✅ At least 1 education entry
- ✅ At least 10 technical skills
- ✅ At least 2 projects

### 3. Descriptions Format
Use newline-separated bullet points for descriptions:
```
Led development of microservices architecture
Implemented CI/CD pipelines with Docker and AWS
Mentored 5 junior developers
```

### 4. Enhanced Content
After uploading sample documents and running profile enhancement:
- Enhanced content stored in `enhanced_summary` and `enhanced_description` fields
- Original content preserved for comparison
- Toggle enhanced content usage in generation requests

### 5. Bulk Operations
Use bulk endpoints for efficiency:
```json
// Add 10 experiences in one request
POST /api/v1/profiles/{id}/experiences
{
  "experiences": [...10 items...]
}
```

**Important**: Do not include `id` fields when creating new items in bulk requests. IDs are auto-generated.

---

## API Standardization Updates

### DELETE Request Format Standardization (November 27, 2025)

All bulk DELETE operations now use a **consistent wrapped format** for request bodies:

| Endpoint | Request Body Format | Status |
|----------|---------------------|--------|
| `DELETE /profiles/{id}/experiences` | `{"experience_ids": [...]}` | ✅ Standardized |
| `DELETE /profiles/{id}/education` | `{"education_ids": [...]}` | ✅ Standardized |
| `DELETE /profiles/{id}/projects` | `{"project_ids": [...]}` | ✅ Standardized |
| `DELETE /profiles/{id}/skills/technical` | `{"skills": [...]}` | ✅ Standardized |
| `DELETE /profiles/{id}/skills/soft` | `{"skills": [...]}` | ✅ Standardized |

**Previous Inconsistency**: Education and Projects used direct list format `["id1", "id2"]`  
**New Standard**: All endpoints use wrapped object format `{"<resource>_ids": ["id1", "id2"]}`

**Example Migration**:
```python
# OLD (Direct list - deprecated)
DELETE /api/v1/profiles/{id}/education
["edu_1", "edu_2"]

# NEW (Wrapped format - current)
DELETE /api/v1/profiles/{id}/education
{"education_ids": ["edu_1", "edu_2"]}
```

---

## Future Enhancements

- [ ] Profile templates (Software Engineer, Designer, etc.)
- [ ] Profile import from LinkedIn
- [ ] Profile export to PDF
- [ ] Profile comparison and versioning
- [ ] Profile sharing and collaboration
- [ ] AI-powered content suggestions
- [ ] ATS keyword optimization analysis

---

**Last Updated**: November 30, 2025
**API Version**: 1.0
**Total Endpoints**: 24
**Status**: Production Ready
**Recent Changes**:
- ✅ **ID Auto-Generation** (Nov 30, 2025): All resource IDs (experiences, education, projects) are now automatically generated as UUIDs by the backend. Clients should never include `id` fields in POST requests.
- ✅ Standardized DELETE request formats across all bulk operations (Nov 27, 2025)
- ✅ Updated response codes for education/projects DELETE (200 OK instead of 204 No Content) (Nov 27, 2025)
