# Profile API Service

**Version**: 1.0
**Base Path**: `/api/v1/profiles`
**Status**: Implemented

## Service Overview

Manages master resume profiles containing personal information, work experience, education, skills, projects, and certifications. Profiles serve as the source data for AI-generated resumes.

## Specification

**Purpose**: Master resume data management
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
Create Profile:
1. Client → POST /profiles {profile_data}
2. API validates JWT token → get user_id
3. API validates profile data (Pydantic)
4. API creates profile record with user_id
5. API creates related records (experiences, education, skills)
6. API ← Profile response with id

Get Profile:
1. Client → GET /profiles/{id}
2. API validates JWT token → get user_id
3. API fetches profile with relationships
4. API verifies profile.user_id == current_user.id
5. API ← Profile with all components

Update Profile:
1. Client → PUT /profiles/{id} {updated_data}
2. API validates JWT token → get user_id
3. API verifies ownership
4. API updates profile and related records
5. API increments version number
6. API ← Updated profile

List Profiles:
1. Client → GET /profiles
2. API validates JWT token → get user_id
3. API fetches profiles where user_id = current_user.id
4. API ← Profile list with pagination
```

## API Contract

### POST /profiles

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
  "experiences": [
    {
      "title": "Senior Software Engineer",
      "company": "Tech Corp",
      "location": "Seattle, WA",
      "start_date": "2021-01-01",
      "end_date": null,
      "is_current": true,
      "description": "Lead development of microservices",
      "achievements": [
        "Improved performance by 40%",
        "Led team of 4 developers"
      ]
    }
  ],
  "education": [
    {
      "institution": "University of Washington",
      "degree": "Bachelor of Science",
      "field_of_study": "Computer Science",
      "start_date": "2015-09-01",
      "end_date": "2019-06-15",
      "gpa": 3.8,
      "honors": ["Dean's List", "Cum Laude"]
    }
  ],
  "skills": {
    "technical": ["Python", "FastAPI", "React", "PostgreSQL"],
    "soft": ["Leadership", "Problem Solving"],
    "languages": [
      {"name": "English", "proficiency": "native"},
      {"name": "Spanish", "proficiency": "conversational"}
    ],
    "certifications": [
      {
        "name": "AWS Solutions Architect",
        "issuer": "Amazon Web Services",
        "date_obtained": "2023-03-15",
        "expiry_date": "2026-03-15",
        "credential_id": "AWS-12345"
      }
    ]
  },
  "projects": [
    {
      "name": "E-commerce Platform",
      "description": "Built scalable e-commerce solution",
      "technologies": ["Python", "Django", "React"],
      "url": "https://github.com/johndoe/ecommerce",
      "start_date": "2020-01-01",
      "end_date": "2020-12-31"
    }
  ]
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "user_id": "user-uuid",
  "personal_info": {...},
  "professional_summary": "...",
  "experiences": [...],
  "education": [...],
  "skills": {...},
  "projects": [...],
  "version": 1,
  "created_at": "2025-10-21T10:00:00Z",
  "updated_at": "2025-10-21T10:00:00Z"
}
```

**Errors**:
- 400: Validation error
- 401: Unauthorized

### GET /profiles

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

### GET /profiles/{id}

**Description**: Get profile details

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK): Full profile object (same as POST response)

**Errors**:
- 404: Profile not found
- 403: Not authorized (not owner)

### PUT /profiles/{id}

**Description**: Update profile (full replacement)

**Headers**: `Authorization: Bearer <token>`

**Request**: Same structure as POST

**Response** (200 OK): Updated profile with incremented version

**Errors**:
- 400: Validation error
- 404: Profile not found
- 403: Not authorized

### DELETE /profiles/{id}

**Description**: Delete profile and all related data

**Headers**: `Authorization: Bearer <token>`

**Response** (204 No Content)

**Errors**:
- 404: Profile not found
- 403: Not authorized

### GET /profiles/me

**Description**: Get current user's active profile

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK): Profile object or 404 if no profile exists

### GET /profiles/{id}/analytics

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
    "projects": 50
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
    "Include project URLs"
  ]
}
```

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
- Support adding/removing list items (experiences, education, skills)
- Auto-save drafts locally before submitting
- Show version number for conflict resolution

## Implementation Notes

### Repository
- `app/infrastructure/repositories/profile_repository.py`
- Uses SQLAlchemy async sessions
- Eager loads relationships with `selectinload()`

### Service
- `app/application/services/profile_service.py`
- Handles business logic and validation

### Database Models
- MasterProfileModel (main profile)
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

### Testing
- Test CRUD operations
- Test ownership verification
- Test relationship loading
- Test validation errors
- Test pagination
