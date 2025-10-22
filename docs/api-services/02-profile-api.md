# Profile API Service

**Version**: 2.1
**Base Path**: `/api/v1/profiles`
**Status**: Partially Implemented ✅ (Core profile CRUD implemented, bulk operations documented, granular component routes pending)
**Test Coverage**: 18 live tests passing (Profile API: 1 test, Auth API: 17 tests)

## Service Overview

Manages master resume profiles containing personal information, work experience, education, skills, projects, certifications, and custom fields. Supports comprehensive profile creation with multiple experiences, education, and projects in a single request. Provides granular CRUD operations for all profile components with bulk operations support (add/update multiple items of the same type simultaneously). Profiles serve as the source data for AI-generated resumes with efficient batch processing capabilities.

**Current Implementation**: Core profile retrieval (GET /profiles/me) implemented and tested. Database schema supports full bulk operations design. Granular component CRUD endpoints designed but routes pending implementation.

## Specification

**Purpose**: Master resume data management with granular CRUD operations
**Authentication**: Required (JWT)
**Authorization**: User can only access their own profiles
**Performance**: <200ms for CRUD operations
**Validation**: Pydantic v2 schemas

## Dependencies

### Internal
- Authentication API: User identity via JWT
- Database: MasterProfileModel, ExperienceModel, EducationModel, SkillModel, ProjectModel
- Repositories: ProfileRepository

### External
None

## Data Flow

```
Create Profile (Designed):
1. Client → POST /profiles {profile_data with experiences, education, projects, custom_fields}
2. API validates JWT token → get user_id
3. API validates profile data (Pydantic) including all nested components
4. API creates profile record with user_id
5. API creates related records (experiences, education, skills, projects) in transaction
6. API stores custom_fields as JSON data
7. API ← Profile response with all components populated

Get Profile (Implemented):
1. Client → GET /profiles/me
2. API validates JWT token → get user_id
3. API retrieves user's profile with JSON fields (personal_info, skills, custom_fields)
4. API ← Profile response with all components populated

Granular Component CRUD (Designed):
1. Client → POST /profiles/{id}/experiences {experience_array}
2. API validates JWT token → get user_id
3. API verifies profile ownership
4. API creates multiple experience records linked to profile
5. API ← Array of experience responses with ids

Bulk Component Updates (Designed):
1. Client → PUT /profiles/{id}/experiences {experience_updates_array}
2. API validates JWT token → get user_id
3. API verifies ownership for all items
4. API updates multiple experience records in transaction
5. API increments profile version number
6. API ← Array of updated experience objects
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

**Request**:
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
  "version": 1,
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
      "personal_info": {
        "full_name": "John Doe",
        "email": "john@example.com",
        "location": "Seattle, WA"
      },
      "version": 1,
      "created_at": "2025-10-21T10:00:00Z",
      "updated_at": "2025-10-21T10:00:00Z"
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 20,
    "offset": 0,
    "has_next": false,
    "has_previous": false
  }
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

**Description**: Update profile (full replacement)

**Headers**: `Authorization: Bearer <token>`

**Request**: Complete profile update with all optional fields
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

**Response** (200 OK): Updated profile with incremented version

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
  "profile_id": "uuid",
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
    "start_date": "2021-01-01",
    "end_date": null,
    "is_current": true,
    "description": "Lead development of microservices architecture",
    "achievements": [
      "Improved system performance by 40%",
      "Led team of 4 developers"
    ]
  },
  {
    "title": "Software Engineer",
    "company": "Startup Inc",
    "location": "San Francisco, CA",
    "start_date": "2019-01-01",
    "end_date": "2020-12-31",
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
    "id": "exp-uuid-1",
    "title": "Senior Software Engineer",
    "company": "Tech Corp",
    "location": "Seattle, WA",
    "start_date": "2021-01-01",
    "end_date": null,
    "is_current": true,
    "description": "Lead development of microservices architecture",
    "achievements": ["Improved system performance by 40%", "Led team of 4 developers"]
  },
  {
    "id": "exp-uuid-2",
    "title": "Software Engineer",
    "company": "Startup Inc",
    "location": "San Francisco, CA",
    "start_date": "2019-01-01",
    "end_date": "2020-12-31",
    "is_current": false,
    "description": "Full-stack development using React and Node.js",
    "achievements": ["Built user-facing features", "Improved application performance"]
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
      "id": "exp-uuid",
      "title": "Senior Software Engineer",
      "company": "Tech Corp",
      "start_date": "2021-01-01",
      "is_current": true,
      "description": "Lead development..."
    }
  ],
  "pagination": {
    "total": 3,
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
    "id": "exp-uuid-1",
    "title": "Senior Software Engineer",
    "company": "Tech Corp",
    "location": "Seattle, WA",
    "start_date": "2021-01-01",
    "end_date": "2023-06-01",
    "is_current": false,
    "description": "Lead development of microservices architecture",
    "achievements": [
      "Improved system performance by 40%",
      "Led team of 4 developers",
      "Implemented CI/CD pipeline"
    ]
  },
  {
    "id": "exp-uuid-2",
    "title": "Principal Engineer",
    "company": "Startup Inc",
    "location": "San Francisco, CA",
    "start_date": "2019-01-01",
    "end_date": "2020-12-31",
    "is_current": false,
    "description": "Full-stack development and team leadership",
    "achievements": [
      "Built user-facing features",
      "Improved application performance",
      "Mentored junior developers"
    ]
  }
]
```

**Response** (200 OK): Array of updated experience objects

#### DELETE /profiles/{profile_id}/experiences

**Description**: Delete one or more work experiences

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of experience IDs to delete
```json
{
  "experience_ids": ["exp-uuid-1", "exp-uuid-2"]
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
    "start_date": "2015-09-01",
    "end_date": "2019-06-15",
    "gpa": 3.8,
    "honors": ["Dean's List", "Summa Cum Laude"]
  },
  {
    "institution": "Stanford University",
    "degree": "Master of Science",
    "field_of_study": "Software Engineering",
    "start_date": "2019-09-01",
    "end_date": "2021-06-15",
    "gpa": 3.9,
    "honors": ["Graduate Research Assistant", "Teaching Assistant"]
  }
]
```

**Response** (201 Created): Array of created education objects

#### PUT /profiles/{profile_id}/education

**Description**: Update one or more education entries (full replacement)

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of education objects with IDs

**Response** (200 OK): Array of updated education objects

#### DELETE /profiles/{profile_id}/education

**Description**: Delete one or more education entries

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of education IDs to delete
```json
{
  "education_ids": ["edu-uuid-1", "edu-uuid-2"]
}
```

**Response** (204 No Content)

### Project CRUD Operations

#### POST /profiles/{profile_id}/projects

**Description**: Add one or more portfolio projects

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of project objects
```json
[
  {
    "name": "E-commerce Platform",
    "description": "Built scalable e-commerce solution with React and Node.js",
    "technologies": ["React", "Node.js", "PostgreSQL", "AWS"],
    "url": "https://github.com/johndoe/ecommerce",
    "start_date": "2020-01-01",
    "end_date": "2020-12-31"
  },
  {
    "name": "AI Chat Application",
    "description": "Real-time chat application with AI-powered responses",
    "technologies": ["Python", "FastAPI", "WebSocket", "OpenAI API"],
    "url": "https://github.com/johndoe/ai-chat",
    "start_date": "2021-03-01",
    "end_date": "2021-08-01"
  },
  {
    "name": "Mobile Fitness Tracker",
    "description": "Cross-platform mobile app for fitness tracking",
    "technologies": ["Flutter", "Firebase", "Dart"],
    "url": "https://github.com/johndoe/fitness-tracker",
    "start_date": "2022-01-01",
    "end_date": "2022-06-01"
  }
]
```

**Response** (201 Created): Array of created project objects

#### PUT /profiles/{profile_id}/projects

**Description**: Update one or more projects (full replacement)

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of project objects with IDs

**Response** (200 OK): Array of updated project objects

#### DELETE /profiles/{profile_id}/projects

**Description**: Delete one or more projects

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of project IDs to delete
```json
{
  "project_ids": ["proj-uuid-1", "proj-uuid-2", "proj-uuid-3"]
}
```

**Response** (204 No Content)

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
  "certifications": [
    {
      "id": "cert-uuid",
      "name": "AWS Solutions Architect",
      "issuer": "Amazon",
      "date_obtained": "2023-01-01",
      "credential_id": "AWS-123"
    }
  ]
}
```

#### PUT /profiles/{profile_id}/skills

**Description**: Update all skills

**Headers**: `Authorization: Bearer <token>`

**Request**: Complete skills object

#### POST /profiles/{profile_id}/skills/technical

**Description**: Add one or more technical skills

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of technical skills
```json
{
  "skills": ["Docker", "Kubernetes", "AWS", "Terraform", "Jenkins"]
}
```

#### DELETE /profiles/{profile_id}/skills/technical

**Description**: Remove one or more technical skills

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of technical skills to remove
```json
{
  "skills": ["Docker", "Jenkins"]
}
```

**Note**: URL encode the skill name (e.g., "C%2B%2B" for "C++")

#### POST /profiles/{profile_id}/skills/soft

**Description**: Add one or more soft skills

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of soft skills
```json
{
  "skills": ["Project Management", "Team Leadership", "Problem Solving", "Public Speaking"]
}
```

#### DELETE /profiles/{profile_id}/skills/soft/{skill}

**Description**: Remove soft skills

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of soft skills to remove

### Certification CRUD Operations

#### POST /profiles/{profile_id}/certifications

**Description**: Add one or more certifications

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of certification objects
```json
[
  {
    "name": "AWS Solutions Architect",
    "issuer": "Amazon Web Services",
    "date_obtained": "2023-01-01",
    "expiry_date": "2026-01-01",
    "credential_id": "AWS-12345"
  },
  {
    "name": "Google Cloud Professional Developer",
    "issuer": "Google",
    "date_obtained": "2022-06-01",
    "expiry_date": "2025-06-01",
    "credential_id": "GCP-67890"
  },
  {
    "name": "Certified Kubernetes Administrator",
    "issuer": "Cloud Native Computing Foundation",
    "date_obtained": "2023-03-01",
    "expiry_date": "2026-03-01",
    "credential_id": "CKA-11111"
  }
]
```

**Response** (201 Created): Array of created certification objects

#### GET /profiles/{profile_id}/certifications

**Description**: List all certifications

**Headers**: `Authorization: Bearer <token>`

#### PUT /profiles/{profile_id}/certifications

**Description**: Update one or more certifications (full replacement)

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of certification objects with IDs

**Response** (200 OK): Array of updated certification objects

#### DELETE /profiles/{profile_id}/certifications

**Description**: Delete one or more certifications

**Headers**: `Authorization: Bearer <token>`

**Request**: Array of certification IDs to delete
```json
{
  "certification_ids": ["cert-uuid-1", "cert-uuid-2", "cert-uuid-3"]
}
```

**Response** (204 No Content)

### Custom Fields Operations

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
  "message": "Custom fields updated successfully",
  "updated_fields": ["hobbies", "achievements", "interests"]
}
```

**Errors**:
- 400: Validation error
- 404: Profile not found
- 403: Not authorized

#### GET /profiles/{profile_id}/custom-fields

**Description**: Get custom fields

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

#### PUT /profiles/{profile_id}/custom-fields

**Description**: Update custom fields (supports bulk updates)

**Headers**: `Authorization: Bearer <token>`

**Request**: JSON object with multiple custom field updates
```json
{
  "achievements": ["Led team of 10 developers", "Increased performance by 40%", "Implemented ML pipeline", "Reduced costs by 25%"],
  "hobbies": ["Photography", "Hiking", "Reading", "Cooking", "Traveling"],
  "interests": ["AI/ML", "Open Source", "Sustainable Technology", "Blockchain", "Quantum Computing"],
  "volunteer_work": ["Code for America", "Local Hackathon Organizer"],
  "publications": ["Published paper on distributed systems", "Blog posts on software architecture"],
  "awards": ["Employee of the Year 2023", "Innovation Award 2022"]
}
```

**Response** (200 OK): Updated custom fields object with all fields

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
  final int version;
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
    required this.version,
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
      version: json['version'],
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
- Show version number for conflict resolution
- **Current Status**: Core profile retrieval implemented, bulk operations designed for future implementation
- **Future**: Allow bulk operations for multiple experiences/education/projects during profile creation
- **Future**: Support batch adding multiple items of the same type (e.g., add 5 projects at once, add 6 experiences at once)
- **Future**: Provide progress indicators for bulk operations
- **Future**: Allow users to edit multiple items simultaneously before saving

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

### Current Implementation Status
- ✅ Core Profile CRUD: GET /profiles/me implemented and tested
- ✅ Database Models: All models defined with JSON storage for flexible data
- ✅ Authentication: JWT-based ownership verification
- ✅ Custom Fields: JSON storage implemented in domain model
- ✅ Bulk Operations: API contract designed for array-based operations
- ⏳ Granular Component Routes: POST/PUT/DELETE for experiences, education, projects, skills pending
- ⏳ Service Layer: Bulk operations methods pending implementation
- ⏳ API Routes: Component-specific endpoints pending implementation

### Testing
- Test CRUD operations
- Test ownership verification
- Test relationship loading
- Test validation errors
- Test pagination
- Test custom fields operations
- Test bulk profile creation with multiple components
- Test bulk operations for experiences, education, projects, and certifications
- Test batch adding/updating multiple items of the same type
- **Live Server Tests**: 18 comprehensive tests covering authentication and profile endpoints
- **Test Coverage**: Core profile operations, ownership verification, relationship loading, validation errors, pagination
- **Authentication**: JWT token validation and authorization checks
- **Error Handling**: 400, 401, 403, 404, 422 status code validation
- **Data Integrity**: Profile creation, updates, and cascading deletes
- **Custom Fields**: JSON storage and retrieval validation
- **Bulk Operations**: Array-based create/update/delete operations for all component types (designed but not yet implemented)