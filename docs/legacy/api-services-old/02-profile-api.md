# Profile API Service

**Version**: 2.2
**Base Path**: `/api/v1/profiles`
**Status**: ✅ **Fully Implemented** (Core profile CRUD, bulk operations, granular component routes, and analytics all implemented and tested)
**Test Coverage**: 39 live tests passing (Profile API: 17 tests including core CRUD, Granular Operations: 13 tests for experiences/education/projects/skills/custom fields, Bulk Operations: 9 tests for batch operations)
**Last Updated**: November 2, 2025 - **Bug fixes**: Profile creation now includes nested arrays, Education endDate optional, Project startDate optional

## Service Overview

Manages master resume profiles containing personal information, work experience, education, skills, projects, certifications, and custom fields.

**Progressive Profile Building**:
- **Required for creation**: Only `personal_info` (name + email)
- **Completely optional**: experiences, education, projects, skills, professional_summary, custom_fields
- **Update anytime**: Users can add/update any component at any time through PUT /profiles/{id}

Supports comprehensive profile creation with multiple experiences, education, and projects in a single request. Provides granular CRUD operations for all profile components with bulk operations support (add/update multiple items of the same type simultaneously). Profiles serve as the source data for AI-generated resumes with efficient batch processing capabilities.

**Current Implementation**: ✅ All endpoints implemented and tested including:
- Core profile CRUD operations (GET /profiles/me, POST/PUT/DELETE /profiles/{id})
- Bulk operations for experiences, education, and projects
- Granular skills management (add/remove individual skills)
- Custom fields operations
- Profile analytics and completeness scoring

## Specification

**Purpose**: Master resume data management with granular CRUD operations
**Authentication**: Required (JWT)
**Authorization**: User can only access their own profiles
**Performance**: <200ms for CRUD operations
**Validation**: Pydantic v2 schemas

## Error Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 201 | Created | Resource successfully created |
| 200 | OK | Request successful |
| 204 | No Content | Delete successful (no response body) |
| 400 | Bad Request | Validation error or malformed request |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | User doesn't own the resource |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | User already has a profile (create only) |
| 422 | Unprocessable Entity | Pydantic validation failed |
| 500 | Internal Server Error | Server error |

## Validation Rules

**Personal Info:**
- `full_name`: Required, 1-100 chars
- `email`: Required, valid email format
- `phone`: Optional, must contain digits if provided
- `location`: Optional, max 100 chars
- `linkedin`/`github`/`website`: Optional, must start with http:// or https://

**Dates:**
- Format: ISO 8601 `YYYY-MM-DD`
- Experience: `start_date` required, `end_date` optional
- Experience: `is_current=true` cannot have `end_date`
- Education: `start_date` required, `end_date` **optional** (as of v2.2)
- Project: `start_date` **optional**, `end_date` optional (as of v2.2)

**Experiences/Education/Projects:**
- All fields in nested arrays are validated on create/update
- IDs auto-generated if not provided (`exp_1`, `edu_1`, `proj_1`, etc.)

**Skills:**
- Technical/Soft: Cannot contain empty strings
- Languages: Proficiency must be: `native`, `fluent`, `conversational`, `basic`
- GPA: Float 0.0-4.0

## Dependencies

### Internal
- Authentication API: User identity via JWT
- Database: MasterProfileModel, ExperienceModel, EducationModel, SkillModel, ProjectModel
- Repositories: ProfileRepository

### External
None

## Data Flow

```
Create Profile (✅ Implemented):
1. Client → POST /profiles {profile_data with experiences, education, projects, custom_fields}
2. API validates JWT token → get user_id
3. API validates profile data (Pydantic) including all nested components
4. API creates profile record with user_id
5. API creates related records (experiences, education, skills, projects) in transaction
6. API stores custom_fields as JSON data
7. API ← Profile response with all components populated

Get Profile (✅ Implemented):
1. Client → GET /profiles/me or GET /profiles/{id}
2. API validates JWT token → get user_id
3. API retrieves user's profile with JSON fields (personal_info, skills, custom_fields)
4. API ← Profile response with all components populated

Bulk Component Operations (✅ Implemented):
1. Client → POST /profiles/{id}/experiences {experience_array}
2. API validates JWT token → get user_id
3. API verifies profile ownership
4. API creates multiple experience records linked to profile
5. API ← Array of experience responses with ids

Granular Skills Management (✅ Implemented):
1. Client → POST /profiles/{id}/skills/technical {skills_array}
2. API validates JWT token → get user_id
3. API verifies profile ownership
4. API adds skills without duplicates
5. API ← Success message with count

Analytics (✅ Implemented):
1. Client → GET /profiles/{id}/analytics
2. API validates JWT token → get user_id
3. API calculates completeness scores and statistics
4. API generates improvement recommendations
5. API ← Analytics response with scores and recommendations
```

## Multiple Profiles Design Decision

**Current Implementation**: Single profile per user
**Rationale**: 
- JobWise mobile app assumes one active profile for resume generation
- Simplifies user experience and data management
- Most users don't need multiple profiles for job applications

**Future Extensibility**: 
- Database schema supports multiple profiles (no unique constraint on user_id)
- API can be extended with profile selection/switching
- Business logic currently prevents multiple profiles but can be modified

**Use Cases for Multiple Profiles** (Future):
- Different job types (entry-level vs senior positions)
- Industry-specific profiles (tech vs non-tech)
- Language variants (English vs local language)
- Draft versions for testing

## API Contract

### Profile CRUD Operations

#### POST /profiles

**Description**: Create new master profile

**Headers**: `Authorization: Bearer <token>`

**Minimal Required Request** (name + email only):
```json
{
  "personal_info": {
    "full_name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Full Request Example** (all optional fields shown):
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
  "professional_summary": "Experienced software engineer with 5+ years...",
  "skills": {
    "technical": ["Python", "FastAPI", "React"],
    "soft": ["Leadership", "Communication"],
    "languages": [
      {"name": "English", "proficiency": "native"},
      {"name": "Spanish", "proficiency": "conversational"}
    ],
    "certifications": [{
      "name": "AWS Solutions Architect",
      "issuer": "Amazon",
      "date_obtained": "2023-01-01",
      "credential_id": "AWS-123"
    }]
  },
  "experiences": [{
    "title": "Senior Software Engineer",
    "company": "Tech Corp",
    "location": "Seattle, WA",
    "start_date": "2021-01-01",
    "end_date": null,
    "is_current": true,
    "description": "Lead development of microservices architecture",
    "achievements": [
      "Improved system performance by 40%",
      "Led team of 4 developers"
    ]
  }],
  "education": [{
    "institution": "University of Washington",
    "degree": "Bachelor of Science",
    "field_of_study": "Computer Science",
    "start_date": "2015-09-01",
    "end_date": "2019-06-15",
    "gpa": 3.8,
    "honors": ["Dean's List", "Summa Cum Laude"]
  }],
  "projects": [{
    "name": "E-commerce Platform",
    "description": "Built scalable e-commerce solution with React and Node.js",
    "technologies": ["React", "Node.js", "PostgreSQL", "AWS"],
    "url": "https://github.com/johndoe/ecommerce",
    "start_date": "2020-01-01",
    "end_date": "2020-12-31"
  }],
  "custom_fields": {
    "achievements": ["Led team of 10 developers", "Increased performance by 40%"],
    "hobbies": ["Photography", "Hiking", "Reading"],
    "interests": ["AI/ML", "Open Source", "Sustainable Technology"]
  }
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "user_id": 123,
  "personal_info": {
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-123-4567",
    "location": "Seattle, WA",
    "linkedin": "https://linkedin.com/in/johndoe",
    "github": "https://github.com/johndoe",
    "website": "https://johndoe.com"
  },
  "professional_summary": "Experienced software engineer with 5+ years...",
  "skills": {
    "technical": ["Python", "FastAPI", "React"],
    "soft": ["Leadership", "Communication"],
    "languages": [
      {"name": "English", "proficiency": "native"},
      {"name": "Spanish", "proficiency": "conversational"}
    ],
    "certifications": [{
      "name": "AWS Solutions Architect",
      "issuer": "Amazon",
      "date_obtained": "2023-01-01",
      "credential_id": "AWS-123"
    }]
  },
  "experiences": [{
    "title": "Senior Software Engineer",
    "company": "Tech Corp",
    "location": "Seattle, WA",
    "start_date": "2021-01-01",
    "end_date": null,
    "is_current": true,
    "description": "Lead development of microservices architecture",
    "achievements": [
      "Improved system performance by 40%",
      "Led team of 4 developers"
    ]
  }],
  "education": [{
    "institution": "University of Washington",
    "degree": "Bachelor of Science",
    "field_of_study": "Computer Science",
    "start_date": "2015-09-01",
    "end_date": "2019-06-15",
    "gpa": 3.8,
    "honors": ["Dean's List", "Summa Cum Laude"]
  }],
  "projects": [{
    "name": "E-commerce Platform",
    "description": "Built scalable e-commerce solution with React and Node.js",
    "technologies": ["React", "Node.js", "PostgreSQL", "AWS"],
    "url": "https://github.com/johndoe/ecommerce",
    "start_date": "2020-01-01",
    "end_date": "2020-12-31"
  }],
  "custom_fields": {
    "achievements": ["Led team of 10 developers", "Increased performance by 40%"],
    "hobbies": ["Photography", "Hiking", "Reading"],
    "interests": ["AI/ML", "Open Source", "Sustainable Technology"]
  },
  "created_at": "2025-10-21T10:00:00Z",
  "updated_at": "2025-10-21T10:00:00Z"
}
```

**Errors**:
- 400: Validation error
- 401: Unauthorized
- 409: User already has a profile

#### GET /profiles

**Description**: List user's profiles

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `limit`: integer (1-100, default: 20)
- `offset`: integer (default: 0)

**Response** (200 OK):
```json
{
  "profiles": [
    {
      "id": "uuid",
      "user_id": 123,
      "personal_info": {
        "full_name": "John Doe",
        "email": "john@example.com",
        "location": "Seattle, WA"
      },
      "professional_summary": "Experienced software engineer...",
      "skills": {
        "technical": ["Python", "FastAPI"],
        "soft": ["Leadership"],
        "languages": [],
        "certifications": []
      },
      "experiences": [],
      "education": [],
      "projects": [],
      "created_at": "2025-10-21T10:00:00Z",
      "updated_at": "2025-10-21T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

#### GET /profiles/{id}

**Description**: Get profile details

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK): Full profile object (same as POST response)

**Errors**:
- 404: Profile not found
- 403: Not authorized (not owner)

#### PUT /profiles/{id}

**Description**: Update profile (supports full or partial updates)

**Headers**: `Authorization: Bearer <token>`

**Note**: You can send only the fields you want to update. All fields except `personal_info` are optional. Empty arrays will replace existing data (use bulk operations to add/remove individual items).

**Request Example** (showing all fields - all optional except personal_info):
```json
{
  "personal_info": {
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-123-4567",
    "location": "San Francisco, CA"
  },
  "professional_summary": "Updated professional summary...",
  "skills": {
    "technical": ["Python", "FastAPI", "React", "TypeScript"],
    "soft": ["Leadership", "Communication", "Problem Solving"],
    "languages": [
      {"name": "English", "proficiency": "native"},
      {"name": "Spanish", "proficiency": "conversational"}
    ],
    "certifications": [{
      "name": "AWS Solutions Architect",
      "issuer": "Amazon",
      "date_obtained": "2023-01-01",
      "credential_id": "AWS-123"
    }]
  },
  "experiences": [{
    "title": "Senior Software Engineer",
    "company": "New Tech Corp",
    "location": "San Francisco, CA",
    "start_date": "2021-01-01",
    "is_current": true,
    "description": "Leading development of AI-powered applications",
    "achievements": [
      "Improved system performance by 40%",
      "Led team of 4 developers",
      "Implemented CI/CD pipeline"
    ]
  }],
  "education": [{
    "institution": "University of Washington",
    "degree": "Bachelor of Science",
    "field_of_study": "Computer Science",
    "start_date": "2015-09-01",
    "end_date": "2019-06-15",
    "gpa": 3.8,
    "honors": ["Dean's List", "Summa Cum Laude"]
  }],
  "projects": [{
    "name": "E-commerce Platform",
    "description": "Built scalable e-commerce solution with React and Node.js",
    "technologies": ["React", "Node.js", "PostgreSQL", "AWS"],
    "url": "https://github.com/johndoe/ecommerce",
    "start_date": "2020-01-01",
    "end_date": "2020-12-31"
  }],
  "custom_fields": {
    "achievements": ["Led team of 10 developers", "Increased performance by 40%", "Implemented ML pipeline"],
    "hobbies": ["Photography", "Hiking", "Reading", "Cooking"],
    "interests": ["AI/ML", "Open Source", "Sustainable Technology", "Blockchain"]
  }
}
```

**Response** (200 OK): Updated profile

**Errors**:
- 400: Validation error
- 404: Profile not found
- 403: Not authorized

#### DELETE /profiles/{id}

**Description**: Delete profile and all related data

**Headers**: `Authorization: Bearer <token>`

**Response** (204 No Content)

**Errors**:
- 404: Profile not found
- 403: Not authorized

#### GET /profiles/me

**Description**: Get current user's active profile

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK): Profile object or 404 if no profile exists

#### GET /profiles/{id}/analytics

**Description**: Profile completeness and quality metrics

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "completeness": {
    "overall": 85,
    "personal_info": 100,
    "professional_summary": 100,
    "experiences": 80,
    "education": 100,
    "skills": 70,
    "projects": 50,
    "custom_fields": 60
  },
  "statistics": {
    "total_experiences": 3,
    "total_education": 2,
    "total_skills": 15,
    "total_projects": 2,
    "years_of_experience": 5.5
  },
  "recommendations": [
    "Add more technical skills",
    "Include project URLs",
    "Add achievements and interests"
  ]
}
```

### Experience CRUD Operations

#### POST /profiles/{profile_id}/experiences

**Description**: Add one or more work experiences

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of experience objects
```json
[
  {
    "title": "Senior Software Engineer",
    "company": "Tech Corp",
    "location": "Seattle, WA",
    "start_date": "2020-01-01",
    "end_date": "2023-12-31",
    "is_current": false,
    "description": "Led development of scalable web applications",
    "achievements": [
      "Increased system performance by 40%",
      "Mentored 5 junior developers"
    ]
  },
  {
    "title": "Software Engineer",
    "company": "Startup Inc",
    "location": "San Francisco, CA",
    "start_date": "2018-01-01",
    "end_date": "2019-12-31",
    "is_current": false,
    "description": "Full-stack development using React and Node.js",
    "achievements": [
      "Built user-facing features",
      "Improved application performance"
    ]
  }
]
```

**Response** (201 Created): Array of created experience objects
```json
[
  {
    "id": "exp_uuid_1",
    "title": "Senior Software Engineer",
    "company": "Tech Corp",
    "location": "Seattle, WA",
    "start_date": "2020-01-01",
    "end_date": "2023-12-31",
    "is_current": false,
    "description": "Led development of scalable web applications",
    "achievements": [
      "Increased system performance by 40%",
      "Mentored 5 junior developers"
    ]
  },
  {
    "id": "exp_uuid_2",
    "title": "Software Engineer",
    "company": "Startup Inc",
    "location": "San Francisco, CA",
    "start_date": "2018-01-01",
    "end_date": "2019-12-31",
    "is_current": false,
    "description": "Full-stack development using React and Node.js",
    "achievements": [
      "Built user-facing features",
      "Improved application performance"
    ]
  }
]
```

#### GET /profiles/{profile_id}/experiences

**Description**: List all experiences for a profile

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `limit`: integer (1-100, default: 50)
- `offset`: integer (default: 0)

**Response** (200 OK):
```json
{
  "experiences": [
    {
      "id": "exp_uuid_1",
      "title": "Senior Software Engineer",
      "company": "Tech Corp",
      "location": "Seattle, WA",
      "start_date": "2020-01-01",
      "end_date": "2023-12-31",
      "is_current": false,
      "description": "Led development of scalable web applications",
      "achievements": [
        "Increased system performance by 40%",
        "Mentored 5 junior developers"
      ]
    }
  ],
  "pagination": {
    "total": 2,
    "limit": 50,
    "offset": 0
  }
}
```

#### PUT /profiles/{profile_id}/experiences

**Description**: Update one or more work experiences (full replacement)

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of experience objects with IDs
```json
[
  {
    "id": "exp_uuid_1",
    "title": "Senior Software Engineer",
    "company": "Tech Corp",
    "location": "Seattle, WA",
    "start_date": "2020-01-01",
    "end_date": "2023-12-31",
    "is_current": false,
    "description": "Led development of scalable web applications",
    "achievements": [
      "Increased system performance by 40%",
      "Mentored 5 junior developers",
      "Implemented CI/CD pipeline"
    ]
  }
]
```

**Response** (200 OK): Array of updated experience objects

#### DELETE /profiles/{profile_id}/experiences

**Description**: Delete one or more work experiences

**Headers**: `Authorization: Bearer <token>`

**Request**:
```json
{
  "experience_ids": ["exp_uuid_1", "exp_uuid_2"]
}
```

**Response** (204 No Content)

### Education CRUD Operations

#### POST /profiles/{profile_id}/education

**Description**: Add one or more education entries

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of education objects
```json
[
  {
    "institution": "University of Washington",
    "degree": "Bachelor of Science",
    "field_of_study": "Computer Science",
    "start_date": "2016-09-01",
    "end_date": "2020-06-01",
    "gpa": 3.8,
    "honors": ["Summa Cum Laude", "Dean's List"]
  },
  {
    "institution": "Stanford University",
    "degree": "Master of Science",
    "field_of_study": "Software Engineering",
    "start_date": "2020-09-01",
    "end_date": "2022-06-01",
    "gpa": 3.9,
    "honors": ["Graduate Research Assistant"]
  }
]
```

**Response** (201 Created): Array of created education objects
```json
[
  {
    "id": "edu_uuid_1",
    "institution": "University of Washington",
    "degree": "Bachelor of Science",
    "field_of_study": "Computer Science",
    "start_date": "2016-09-01",
    "end_date": "2020-06-01",
    "gpa": 3.8,
    "honors": ["Summa Cum Laude", "Dean's List"]
  },
  {
    "id": "edu_uuid_2",
    "institution": "Stanford University",
    "degree": "Master of Science",
    "field_of_study": "Software Engineering",
    "start_date": "2020-09-01",
    "end_date": "2022-06-01",
    "gpa": 3.9,
    "honors": ["Graduate Research Assistant"]
  }
]
```

#### PUT /profiles/{profile_id}/education

**Description**: Update one or more education entries (full replacement)

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of education objects with IDs
```json
[
  {
    "id": "edu_uuid_1",
    "institution": "University of Washington",
    "degree": "Bachelor of Science",
    "field_of_study": "Computer Science",
    "start_date": "2016-09-01",
    "end_date": "2020-06-01",
    "gpa": 3.8,
    "honors": ["Summa Cum Laude", "Dean's List", "Magna Cum Laude"]
  }
]
```

**Response** (200 OK): Array of updated education objects

#### DELETE /profiles/{profile_id}/education

**Description**: Delete one or more education entries

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of education IDs to delete
```json
["edu_uuid_1", "edu_uuid_2"]
```

**Response** (200 OK):
```json
{
  "message": "Deleted 2 education entries successfully"
}
```

### Project CRUD Operations

#### POST /profiles/{profile_id}/projects

**Description**: Add one or more portfolio projects

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of project objects
```json
[
  {
    "name": "E-commerce Platform",
    "description": "Built a scalable e-commerce platform handling 10k+ transactions daily",
    "technologies": ["Python", "FastAPI", "PostgreSQL", "Redis"],
    "url": "https://github.com/user/ecommerce",
    "start_date": "2022-01-01",
    "end_date": "2022-06-01"
  },
  {
    "name": "AI Chat Application",
    "description": "Real-time chat application with AI-powered responses",
    "technologies": ["Python", "FastAPI", "WebSocket", "OpenAI API"],
    "url": "https://github.com/user/ai-chat",
    "start_date": "2022-07-01",
    "end_date": "2022-12-01"
  }
]
```

**Response** (201 Created): Array of created project objects
```json
[
  {
    "id": "proj_uuid_1",
    "name": "E-commerce Platform",
    "description": "Built a scalable e-commerce platform handling 10k+ transactions daily",
    "technologies": ["Python", "FastAPI", "PostgreSQL", "Redis"],
    "url": "https://github.com/user/ecommerce",
    "start_date": "2022-01-01",
    "end_date": "2022-06-01"
  },
  {
    "id": "proj_uuid_2",
    "name": "AI Chat Application",
    "description": "Real-time chat application with AI-powered responses",
    "technologies": ["Python", "FastAPI", "WebSocket", "OpenAI API"],
    "url": "https://github.com/user/ai-chat",
    "start_date": "2022-07-01",
    "end_date": "2022-12-01"
  }
]
```

#### PUT /profiles/{profile_id}/projects

**Description**: Update one or more projects (full replacement)

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of project objects with IDs
```json
[
  {
    "id": "proj_uuid_1",
    "name": "E-commerce Platform",
    "description": "Built a scalable e-commerce platform handling 10k+ transactions daily with microservices architecture",
    "technologies": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
    "url": "https://github.com/user/ecommerce",
    "start_date": "2022-01-01",
    "end_date": "2022-06-01"
  }
]
```

**Response** (200 OK): Array of updated project objects

#### DELETE /profiles/{profile_id}/projects

**Description**: Delete one or more projects

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of project IDs to delete
```json
["proj_uuid_1", "proj_uuid_2"]
```

**Response** (200 OK):
```json
{
  "message": "Deleted 2 projects successfully"
}
```

### Skills CRUD Operations

#### GET /profiles/{profile_id}/skills

**Description**: Get all skills

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "technical": ["Python", "FastAPI", "React"],
  "soft": ["Leadership", "Communication"],
  "languages": [
    {"name": "English", "proficiency": "native"},
    {"name": "Spanish", "proficiency": "conversational"}
  ],
  "certifications": [{
    "name": "AWS Solutions Architect",
    "issuer": "Amazon",
    "date_obtained": "2023-01-01",
    "expiry_date": "2026-01-01",
    "credential_id": "AWS-12345"
  }]
}
```

#### PUT /profiles/{profile_id}/skills

**Description**: Update all skills (full replacement)

**Headers**: `Authorization: Bearer <token>`

**Request**: Complete skills object
```json
{
  "technical": ["Python", "FastAPI", "React", "TypeScript"],
  "soft": ["Leadership", "Communication", "Problem Solving"],
  "languages": [
    {"name": "English", "proficiency": "native"},
    {"name": "Spanish", "proficiency": "conversational"}
  ],
  "certifications": [{
    "name": "AWS Solutions Architect",
    "issuer": "Amazon",
    "date_obtained": "2023-01-01",
    "expiry_date": "2026-01-01",
    "credential_id": "AWS-12345"
  }]
}
```

**Response** (200 OK):
```json
{
  "message": "Skills updated successfully"
}
```

#### POST /profiles/{profile_id}/skills/technical

**Description**: Add one or more technical skills

**Headers**: `Authorization: Bearer <token>`

**Request**: 
```json
{
  "skills": ["Docker", "Kubernetes", "AWS"]
}
```

**Response** (200 OK):
```json
{
  "message": "3 technical skills added successfully"
}
```

#### DELETE /profiles/{profile_id}/skills/technical

**Description**: Remove one or more technical skills

**Headers**: `Authorization: Bearer <token>`

**Request**: 
```json
{
  "skills": ["Docker", "AWS"]
}
```

**Response** (200 OK):
```json
{
  "message": "2 technical skills removed successfully"
}
```

#### POST /profiles/{profile_id}/skills/soft

**Description**: Add one or more soft skills

**Headers**: `Authorization: Bearer <token>`

**Request**: 
```json
{
  "skills": ["Project Management", "Team Leadership"]
}
```

**Response** (200 OK):
```json
{
  "message": "2 soft skills added successfully"
}
```

#### DELETE /profiles/{profile_id}/skills/soft

**Description**: Remove one or more soft skills

**Headers**: `Authorization: Bearer <token>`

**Request**: 
```json
{
  "skills": ["Project Management"]
}
```

**Response** (200 OK):
```json
{
  "message": "1 soft skills removed successfully"
}
```

### Certification CRUD Operations

**Note**: Certification operations are not yet implemented. Certifications are currently managed as part of the skills object in profile creation and updates.

### Custom Fields Operations

#### GET /profiles/{profile_id}/custom-fields

**Description**: Get custom fields for a profile

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "achievements": ["Led team of 10", "40% performance improvement"],
  "hobbies": ["Photography", "Hiking"],
  "interests": ["AI/ML", "Open Source"],
  "additional_info": "Custom field content"
}
```

#### POST /profiles/{profile_id}/custom-fields

**Description**: Add or update custom fields for a profile

**Headers**: `Authorization: Bearer <token>`

**Request**:
```json
{
  "fields": [
    {"key": "hobbies", "value": ["reading", "gaming", "photography"]},
    {"key": "achievements", "value": ["Employee of the Month", "Hackathon Winner"]},
    {"key": "interests", "value": ["AI/ML", "Open Source"]}
  ]
}
```

**Response** (201 Created):
```json
{
  "message": "Successfully updated 3 custom fields",
  "updated_fields": ["hobbies", "achievements", "interests"]
}
```

#### PUT /profiles/{profile_id}/custom-fields

**Description**: Update all custom fields (full replacement)

**Headers**: `Authorization: Bearer <token>`

**Request**: Complete custom fields object
```json
{
  "achievements": ["Led team of 10 developers", "Increased performance by 40%", "Implemented ML pipeline"],
  "hobbies": ["Photography", "Hiking", "Reading", "Cooking"],
  "interests": ["AI/ML", "Open Source", "Sustainable Technology", "Blockchain"],
  "volunteer_work": ["Code for America", "Local Hackathon Organizer"],
  "publications": ["Published paper on distributed systems", "Blog posts on software architecture"],
  "awards": ["Employee of the Year 2023", "Innovation Award 2022"]
}
```

**Response** (200 OK): Updated custom fields object

## Mobile Integration Notes

### Profile Model
```dart
class Profile {
  final String id;
  final String userId;
  final PersonalInfo personalInfo;
  final String? professionalSummary;
  final List<Experience> experiences;
  final List<Education> education;
  final Skills skills;
  final List<Project> projects;
  final Map<String, dynamic> customFields;
  final DateTime createdAt;
  final DateTime updatedAt;

  Profile({
    required this.id,
    required this.userId,
    required this.personalInfo,
    this.professionalSummary,
    this.experiences = const [],
    this.education = const [],
    required this.skills,
    this.projects = const [],
    this.customFields = const {},
    required this.createdAt,
    required this.updatedAt,
  });

  factory Profile.fromJson(Map<String, dynamic> json) {
    return Profile(
      id: json['id'],
      userId: json['user_id'],
      personalInfo: PersonalInfo.fromJson(json['personal_info']),
      professionalSummary: json['professional_summary'],
      experiences: (json['experiences'] as List?)
          ?.map((e) => Experience.fromJson(e))
          .toList() ?? [],
      education: (json['education'] as List?)
          ?.map((e) => Education.fromJson(e))
          .toList() ?? [],
      skills: Skills.fromJson(json['skills']),
      projects: (json['projects'] as List?)
          ?.map((e) => Project.fromJson(e))
          .toList() ?? [],
      customFields: json['custom_fields'] ?? {},
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() => {
    'personal_info': personalInfo.toJson(),
    'professional_summary': professionalSummary,
    'experiences': experiences.map((e) => e.toJson()).toList(),
    'education': education.map((e) => e.toJson()).toList(),
    'skills': skills.toJson(),
    'projects': projects.map((e) => e.toJson()).toList(),
    'custom_fields': customFields,
  };
}
```

### Profile Service
```dart
class ProfileService {
  final ApiClient _client;

  Future<Profile> createProfile(Profile profile) async {
    final response = await _client.post('/profiles', data: profile.toJson());
    return Profile.fromJson(response.data);
  }

  Future<List<Profile>> getProfiles({int limit = 20, int offset = 0}) async {
    final response = await _client.get('/profiles', queryParameters: {
      'limit': limit,
      'offset': offset,
    });
    return (response.data['profiles'] as List)
        .map((json) => Profile.fromJson(json))
        .toList();
  }

  Future<Profile> getProfile(String id) async {
    final response = await _client.get('/profiles/$id');
    return Profile.fromJson(response.data);
  }

  Future<Profile> updateProfile(String id, Profile profile) async {
    final response = await _client.put('/profiles/$id', data: profile.toJson());
    return Profile.fromJson(response.data);
  }

  Future<void> deleteProfile(String id) async {
    await _client.delete('/profiles/$id');
  }
}
```

### Local Caching
Consider caching profiles locally:
- Use Hive or SQLite for offline access
- Sync on network availability
- Show cached data with "Syncing..." indicator

### Form Validation
- Validate phone numbers with regex
- Validate email format
- Validate URLs (LinkedIn, GitHub, website)
- Validate date ranges (start_date < end_date)
- Show character counts for text fields

### UI Considerations
- Show profile completeness percentage
- Use date pickers for date fields
- Support adding/removing list items (experiences, education, skills, projects)
- Support custom fields with dynamic key-value pairs
- Auto-save drafts locally before submitting
- **Current Status**: ✅ All endpoints implemented and tested including core CRUD, bulk operations, granular skills management, custom fields, and analytics
- **Future**: Enhanced features like profile versioning, advanced analytics, and integration with AI generation pipeline

## Implementation Notes

### Repository
- `app/infrastructure/repositories/profile_repository.py`
- Uses SQLAlchemy async sessions
- Eager loads relationships with `selectinload()`

### Service
- `app/application/services/profile_service.py`
- Handles business logic and validation

### Database Models
- MasterProfileModel (main profile with JSON fields for personal_info, skills, and custom_fields)
- ExperienceModel (work history)
- EducationModel (academic background)
- SkillModel (skills and certifications)
- ProjectModel (portfolio projects)

### Validation Rules
- Email: Valid email format
- Phone: International format supported
- URLs: Valid HTTP/HTTPS
- Dates: ISO 8601 format
- Text limits enforced server-side

### Current Implementation Status (v2.2 - November 2, 2025)
- ✅ **Core Profile CRUD**: POST /profiles, GET /profiles/me, GET /profiles/{id}, PUT /profiles/{id}, DELETE /profiles/{id} implemented and tested
- ✅ **Bulk Operations**: POST/PUT/DELETE for experiences, education, and projects fully implemented and tested
- ✅ **Granular Skills Management**: GET/PUT /skills, POST/DELETE /skills/technical, POST/DELETE /skills/soft implemented
- ✅ **Custom Fields**: GET/POST/PUT /custom-fields operations fully implemented
- ✅ **Analytics**: GET /profiles/{id}/analytics with completeness scoring implemented
- ✅ **Authentication**: JWT-based ownership verification for all endpoints
- ✅ **Database Models**: All models with JSON storage for flexible data implemented
- ✅ **Service Layer**: Business logic and validation fully implemented
- ✅ **API Routes**: All component-specific endpoints implemented and tested

### Recent Bug Fixes (v2.2)
1. **Profile Creation Fixed** - Now includes experiences/education/projects from create request (previously ignored)
2. **Education `end_date` Optional** - Changed from required to optional (supports "currently enrolled")
3. **Project `start_date` Optional** - Changed from required to optional (supports projects without start dates)

### Testing

#### Current Test Coverage (✅ Implemented)
- **Live Server Tests**: 39 comprehensive tests passing
  - Profile API: 17 tests (core CRUD operations)
  - Granular Operations: 13 tests (experiences, education, projects, skills, custom fields)
  - Bulk Operations: 9 tests (batch add/update operations for experiences, education, projects)
- **Core Profile Operations**: GET /profiles/me with JWT authentication and ownership verification
- **Bulk Operations**: Full CRUD testing for experiences, education, and projects
- **Granular Operations**: Individual component management (add/remove skills, custom fields)
- **Authentication**: JWT token validation and authorization checks
- **Error Handling**: 400, 401, 403, 404, 422 status code validation
- **Data Integrity**: Profile retrieval with JSON field storage validation
- **Custom Fields**: JSON storage and retrieval validation

#### Test Strategy
- **Unit Tests**: Individual service methods and repository operations
- **Integration Tests**: API endpoints with database interactions
- **Live Server Tests**: End-to-end testing with actual HTTP requests
- **Authentication Tests**: JWT token validation and authorization flows
- **Validation Tests**: Pydantic schema validation and error responses
- **Performance Tests**: Response times and concurrent user handling
- **Data Integrity Tests**: Transaction handling and cascading operations

#### Test Environment
- **Database**: SQLite for testing (in-memory for unit tests, file-based for integration)
- **Authentication**: Mock JWT tokens for unit tests, real tokens for integration tests
- **Fixtures**: Pre-defined test data for profiles, users, and related entities
- **Coverage**: Target 90%+ code coverage for implemented features