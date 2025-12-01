# Profile Management Feature

**At a Glance (For AI Agents)**
- **Feature Name**: Profile Management (Flutter front-end)
- **Primary Role**: Manage the master resume profile that feeds all AI ranking and generation flows.
- **Key Files**: `lib/models/profile.dart`, `lib/models/experience.dart`, `lib/models/education.dart`, `lib/models/project.dart`, `lib/models/skills.dart`, `lib/providers/profile/profile_state.dart`, `lib/providers/profile/profile_notifier.dart`, `lib/services/api/profiles_api_client.dart`
- **Backend Contract**: `../api-services/02-profile-api.md` (24 endpoints for profile, experiences, education, projects, skills, custom fields, analytics).
- **Main Screens**: `ProfileViewScreen`, `ProfileEditScreen`, `SettingsScreen`.

**Related Docs (Navigation Hints)**
- Backend: `../api-services/02-profile-api.md`.
- AI & generation: `../api-services/04b-ai-generation-api.md`, `../api-services/04-v3-generation-api.md`, mobile `04b-ai-generation-feature.md`, `04-generation-feature.md`.
- Samples & jobs: `04a-sample-upload-feature.md`, `03-job-browsing-feature.md`.

**Key Field / Property Semantics**
- `Profile.id` ↔ backend `id`: Primary identifier used when calling nested resources (`/profiles/{id}/experiences`, etc.).
- `Profile.personalInfo` ↔ `personal_info` object; this is what gets surfaced in generated resumes/cover letters.
- `Profile.enhancedSummary` ↔ backend `enhanced_summary`: AI-enriched summary; used by generation as a higher-quality source when present.
- `Skills.technical` / `soft` / `languages` / `certifications`: Mirror backend `skills` object; incomplete lists are valid and safe to send.
- `ProfileState.completenessScore` ↔ analytics `completeness_score`; read-only signal to drive UI indicators, not user-editable.

**Backend API**: [Profile API](../api-services/02-profile-api.md)
**Base Path**: `/api/v1/profiles`
**Status**: ✅ Fully Implemented
**Last Updated**: November 2025

---

## Overview

The Profile Management feature allows users to create and maintain their master resume profile, which serves as the central repository for all career information used in AI-powered document generation.

### User Stories

**As a user**, I want to:
- Create a comprehensive master resume profile with all my career information
- Edit my profile in a structured, multi-step form
- Add, edit, and remove work experiences with descriptions
- Track my education history with degrees and honors
- List my technical and soft skills
- Showcase my projects with links and descriptions
- See my profile completeness score
- Upload sample documents to teach the AI my writing style

---

## Screens

### 1. ProfileViewScreen

**Route**: `/profile`
**File**: `lib/screens/profile/profile_view_screen.dart`

**UI Components**:
- Profile header (name, email, location)
- Profile completeness indicator (circular progress)
- "Edit Profile" button
- Collapsible sections:
  - Personal Information
  - Professional Summary
  - Work Experience (cards with expand/collapse)
  - Education (cards)
  - Skills (chips grouped by type)
  - Projects (cards with links)
  - Certifications (list with dates)

**User Flow**:
```
1. Screen loads → fetch profile data
2. Display loading spinner while fetching
3. Show profile with collapsible sections
4. Tap "Edit Profile" → navigate to ProfileEditScreen
5. Pull-to-refresh to reload profile
```

### 2. ProfileEditScreen (Multi-Step Form)

**Route**: `/profile/edit`
**File**: `lib/screens/profile/profile_edit_screen.dart`

**Form Steps**:
1. **Personal Information** (Step 1/5)
   - Full name, email, phone
   - Location, LinkedIn, GitHub, website

2. **Experiences** (Step 2/5)
   - List of experience cards
   - Add/edit/delete experiences
   - Reorder experiences

3. **Education** (Step 3/5)
   - List of education entries
   - Add/edit/delete education

4. **Skills** (Step 4/5)
   - Technical skills (chips with add/remove)
   - Soft skills (chips)
   - Languages with proficiency
   - Certifications

5. **Projects** (Step 5/5)
   - List of project cards
   - Add/edit/delete projects

**UI Components**:
- Stepper indicator (1/5, 2/5, etc.)
- "Previous" and "Next" buttons
- "Save & Exit" button (saves draft)
- "Cancel" button (confirms before discarding)

**User Flow**:
```
1. User taps "Edit Profile"
2. Load existing profile data into form
3. Navigate through steps with Next/Previous
4. Validate each step before advancing
5. On final step: "Save Profile" button
6. Submit all changes to API
7. Show success message and return to ProfileViewScreen
```

### 3. SettingsScreen

**Route**: `/settings`
**File**: `lib/screens/settings/settings_screen.dart`

**UI Components**:
- Account section:
  - Email (read-only)
  - Full name (editable)
  - Change password button
- Preferences:
  - Date format (US, European, ISO)
  - Theme (Light, Dark, System)
- Data management:
  - Export profile data
  - Delete account
- About:
  - App version
  - Privacy policy link
  - Terms of service link

---

## Backend API Integration

### API Endpoints (24 total)

#### Profile CRUD

**1. POST /api/v1/profiles** - Create profile

Request:
```dart
final profile = await profileApiClient.createProfile(
  personalInfo: PersonalInfo(
    fullName: 'John Doe',
    email: 'john@example.com',
    phone: '+1-555-123-4567',
    location: 'Seattle, WA',
  ),
  professionalSummary: 'Senior Software Engineer...',
  skills: Skills(
    technical: ['Python', 'FastAPI', 'React'],
    soft: ['Leadership', 'Communication'],
  ),
);
```

**2. GET /api/v1/profiles/me** - Get primary profile

Request:
```dart
final profile = await profileApiClient.getMyProfile();
```

Response:
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
    "soft": ["Leadership", "Communication"],
    "languages": [
      {"name": "English", "proficiency": "native"}
    ],
    "certifications": []
  },
  "custom_fields": {},
  "is_primary": true,
  "created_at": "2025-11-15T10:30:00Z",
  "updated_at": "2025-11-15T10:30:00Z"
}
```

**3. PUT /api/v1/profiles/{id}** - Update profile

**4. DELETE /api/v1/profiles/{id}** - Delete profile

**5. GET /api/v1/profiles/{id}/analytics** - Get completeness score

Response (example):
```json
{
  "completeness_score": 85,
  "missing_sections": ["projects", "certifications"],
  "recommendations": [
    "Add at least 2 projects to showcase your work",
    "Include professional certifications"
  ]
}
```

The backend may add additional analytics fields over time (for example, new counters or trend metrics). The mobile app should treat unknown fields as optional and safely ignore any extra properties it does not use.

#### Experiences (Bulk Operations)

**6. POST /api/v1/profiles/{id}/experiences** - Add experiences

Request (Single):
```json
{
  "experience": {
    "title": "Senior Software Engineer",
    "company": "TechCorp",
    "location": "Seattle, WA",
    "start_date": "2020-01-15",
    "end_date": null,
    "is_current": true,
    "description": "Led development of microservices architecture...",
    "technologies": ["Python", "FastAPI", "Docker", "AWS"]
  }
}
```

Request (Bulk):
```json
{
  "experiences": [
    {
      "title": "Senior Software Engineer",
      "company": "TechCorp",
      ...
    },
    {
      "title": "Software Engineer",
      "company": "StartupInc",
      ...
    }
  ]
}
```

**7. GET /api/v1/profiles/{id}/experiences** - Get all experiences

Response:
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
      "description": "Led development of scalable web applications",
      "enhanced_description": null,
      "technologies": ["Python", "FastAPI"],
      "display_order": 0
    }
  ],
  "total": 4
}
```

**8. PUT /api/v1/profiles/{id}/experiences** - Update experiences (bulk)

**9. DELETE /api/v1/profiles/{id}/experiences** - Delete experiences

Request:
```json
{
  "experience_ids": ["uuid1", "uuid2"]
}
```

#### Education (Bulk Operations)

**10. POST /api/v1/profiles/{id}/education** - Add education entries

Request:
```json
{
  "education": {
    "institution": "University of Washington",
    "degree": "Bachelor of Science",
    "field_of_study": "Computer Science",
    "start_date": "2012-09-01",
    "end_date": "2016-06-15",
    "gpa": 3.8,
    "honors": ["Magna Cum Laude", "Dean's List"]
  }
}
```

**11. PUT /api/v1/profiles/{id}/education** - Update education

**12. DELETE /api/v1/profiles/{id}/education** - Delete education

#### Projects (Bulk Operations)

**13. POST /api/v1/profiles/{id}/projects** - Add projects

Request:
```json
{
  "project": {
    "name": "JobWise AI",
    "description": "AI-powered job application assistant",
    "technologies": ["Flutter", "FastAPI", "Groq"],
    "url": "https://github.com/johndoe/jobwise",
    "start_date": "2025-01-01",
    "end_date": "2025-11-01"
  }
}
```

**14. PUT /api/v1/profiles/{id}/projects** - Update projects

**15. DELETE /api/v1/profiles/{id}/projects** - Delete projects

#### Skills Management

**16. GET /api/v1/profiles/{id}/skills** - Get all skills

**17. PUT /api/v1/profiles/{id}/skills** - Update all skills

Request:
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

**18. POST /api/v1/profiles/{id}/skills/technical** - Add technical skills

Request:
```json
{
  "skills": ["Kubernetes", "Terraform"]
}
```

**19. DELETE /api/v1/profiles/{id}/skills/technical** - Remove technical skills

**20. POST /api/v1/profiles/{id}/skills/soft** - Add soft skills

**21. DELETE /api/v1/profiles/{id}/skills/soft** - Remove soft skills

#### Custom Fields

**22. GET /api/v1/profiles/{id}/custom-fields** - Get custom fields

**23. POST /api/v1/profiles/{id}/custom-fields** - Add custom fields

**24. PUT /api/v1/profiles/{id}/custom-fields** - Update custom fields

---

## Data Models

### Profile

**File**: `lib/models/profile.dart`

```dart
class Profile {
  final String id;
  final int userId;
  final PersonalInfo personalInfo;
  final String? professionalSummary;
  final String? enhancedSummary;
  final Skills skills;
  final Map<String, dynamic> customFields;
  final bool isPrimary;
  final DateTime createdAt;
  final DateTime updatedAt;

  Profile({
    required this.id,
    required this.userId,
    required this.personalInfo,
    this.professionalSummary,
    this.enhancedSummary,
    required this.skills,
    this.customFields = const {},
    this.isPrimary = true,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Profile.fromJson(Map<String, dynamic> json) {
    return Profile(
      id: json['id'],
      userId: json['user_id'],
      personalInfo: PersonalInfo.fromJson(json['personal_info']),
      professionalSummary: json['professional_summary'],
      enhancedSummary: json['enhanced_summary'],
      skills: Skills.fromJson(json['skills']),
      customFields: json['custom_fields'] ?? {},
      isPrimary: json['is_primary'] ?? true,
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'personal_info': personalInfo.toJson(),
      'professional_summary': professionalSummary,
      'enhanced_summary': enhancedSummary,
      'skills': skills.toJson(),
      'custom_fields': customFields,
      'is_primary': isPrimary,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  Profile copyWith({
    String? id,
    PersonalInfo? personalInfo,
    String? professionalSummary,
    Skills? skills,
  }) {
    return Profile(
      id: id ?? this.id,
      userId: userId,
      personalInfo: personalInfo ?? this.personalInfo,
      professionalSummary: professionalSummary ?? this.professionalSummary,
      enhancedSummary: enhancedSummary,
      skills: skills ?? this.skills,
      customFields: customFields,
      isPrimary: isPrimary,
      createdAt: createdAt,
      updatedAt: updatedAt,
    );
  }
}
```

### PersonalInfo

```dart
class PersonalInfo {
  final String fullName;
  final String email;
  final String? phone;
  final String? location;
  final String? linkedin;
  final String? github;
  final String? website;

  PersonalInfo({
    required this.fullName,
    required this.email,
    this.phone,
    this.location,
    this.linkedin,
    this.github,
    this.website,
  });

  factory PersonalInfo.fromJson(Map<String, dynamic> json) {
    return PersonalInfo(
      fullName: json['full_name'],
      email: json['email'],
      phone: json['phone'],
      location: json['location'],
      linkedin: json['linkedin'],
      github: json['github'],
      website: json['website'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'full_name': fullName,
      'email': email,
      'phone': phone,
      'location': location,
      'linkedin': linkedin,
      'github': github,
      'website': website,
    };
  }
}
```

### Experience

```dart
class Experience {
  final String? id;
  final String title;
  final String company;
  final String? location;
  final DateTime startDate;
  final DateTime? endDate;
  final bool isCurrent;
  final String description;
  final String? enhancedDescription;
  final List<String> technologies;

  Experience({
    this.id,
    required this.title,
    required this.company,
    this.location,
    required this.startDate,
    this.endDate,
    this.isCurrent = false,
    required this.description,
    this.enhancedDescription,
    this.technologies = const [],
  });

  factory Experience.fromJson(Map<String, dynamic> json) {
    return Experience(
      id: json['id'],
      title: json['title'],
      company: json['company'],
      location: json['location'],
      startDate: DateTime.parse(json['start_date']),
      endDate: json['end_date'] != null ? DateTime.parse(json['end_date']) : null,
      isCurrent: json['is_current'] ?? false,
      description: json['description'],
      enhancedDescription: json['enhanced_description'],
      technologies: List<String>.from(json['technologies'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'title': title,
      'company': company,
      'location': location,
      'start_date': startDate.toIso8601String().split('T')[0],
      'end_date': endDate?.toIso8601String().split('T')[0],
      'is_current': isCurrent,
      'description': description,
      'enhanced_description': enhancedDescription,
      'technologies': technologies,
    };
  }
}
```

### Education

```dart
class Education {
  final String? id;
  final String institution;
  final String degree;
  final String fieldOfStudy;
  final DateTime startDate;
  final DateTime? endDate;
  final double? gpa;
  final List<String> honors;

  Education({
    this.id,
    required this.institution,
    required this.degree,
    required this.fieldOfStudy,
    required this.startDate,
    this.endDate,
    this.gpa,
    this.honors = const [],
  });

  factory Education.fromJson(Map<String, dynamic> json) {
    return Education(
      id: json['id'],
      institution: json['institution'],
      degree: json['degree'],
      fieldOfStudy: json['field_of_study'],
      startDate: DateTime.parse(json['start_date']),
      endDate: json['end_date'] != null ? DateTime.parse(json['end_date']) : null,
      gpa: json['gpa']?.toDouble(),
      honors: List<String>.from(json['honors'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'institution': institution,
      'degree': degree,
      'field_of_study': fieldOfStudy,
      'start_date': startDate.toIso8601String().split('T')[0],
      'end_date': endDate?.toIso8601String().split('T')[0],
      'gpa': gpa,
      'honors': honors,
    };
  }
}
```

### Project

```dart
class Project {
  final String? id;
  final String name;
  final String description;
  final String? enhancedDescription;
  final List<String> technologies;
  final String? url;
  final DateTime? startDate;
  final DateTime? endDate;

  Project({
    this.id,
    required this.name,
    required this.description,
    this.enhancedDescription,
    this.technologies = const [],
    this.url,
    this.startDate,
    this.endDate,
  });

  factory Project.fromJson(Map<String, dynamic> json) {
    return Project(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      enhancedDescription: json['enhanced_description'],
      technologies: List<String>.from(json['technologies'] ?? []),
      url: json['url'],
      startDate: json['start_date'] != null ? DateTime.parse(json['start_date']) : null,
      endDate: json['end_date'] != null ? DateTime.parse(json['end_date']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'name': name,
      'description': description,
      'enhanced_description': enhancedDescription,
      'technologies': technologies,
      'url': url,
      'start_date': startDate?.toIso8601String().split('T')[0],
      'end_date': endDate?.toIso8601String().split('T')[0],
    };
  }
}
```

### Skills

```dart
class Skills {
  final List<String> technical;
  final List<String> soft;
  final List<Language> languages;
  final List<Certification> certifications;

  Skills({
    this.technical = const [],
    this.soft = const [],
    this.languages = const [],
    this.certifications = const [],
  });

  factory Skills.fromJson(Map<String, dynamic> json) {
    return Skills(
      technical: List<String>.from(json['technical'] ?? []),
      soft: List<String>.from(json['soft'] ?? []),
      languages: (json['languages'] as List?)
          ?.map((e) => Language.fromJson(e))
          .toList() ?? [],
      certifications: (json['certifications'] as List?)
          ?.map((e) => Certification.fromJson(e))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'technical': technical,
      'soft': soft,
      'languages': languages.map((e) => e.toJson()).toList(),
      'certifications': certifications.map((e) => e.toJson()).toList(),
    };
  }
}

class Language {
  final String name;
  final String proficiency; // native, fluent, conversational, basic

  Language({required this.name, required this.proficiency});

  factory Language.fromJson(Map<String, dynamic> json) {
    return Language(
      name: json['name'],
      proficiency: json['proficiency'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'proficiency': proficiency,
    };
  }
}

class Certification {
  final String name;
  final String issuer;
  final DateTime? dateObtained;
  final String? credentialId;

  Certification({
    required this.name,
    required this.issuer,
    this.dateObtained,
    this.credentialId,
  });

  factory Certification.fromJson(Map<String, dynamic> json) {
    return Certification(
      name: json['name'],
      issuer: json['issuer'],
      dateObtained: json['date_obtained'] != null
          ? DateTime.parse(json['date_obtained'])
          : null,
      credentialId: json['credential_id'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'issuer': issuer,
      'date_obtained': dateObtained?.toIso8601String().split('T')[0],
      'credential_id': credentialId,
    };
  }
}
```

---

## State Management

### ProfileState

**File**: `lib/providers/profile/profile_state.dart`

```dart
class ProfileState {
  final Profile? profile;
  final List<Experience> experiences;
  final List<Education> education;
  final List<Project> projects;
  final bool isLoading;
  final String? errorMessage;
  final int? completenessScore;

  ProfileState({
    this.profile,
    this.experiences = const [],
    this.education = const [],
    this.projects = const [],
    this.isLoading = false,
    this.errorMessage,
    this.completenessScore,
  });

  factory ProfileState.initial() {
    return ProfileState();
  }

  ProfileState copyWith({
    Profile? profile,
    List<Experience>? experiences,
    List<Education>? education,
    List<Project>? projects,
    bool? isLoading,
    String? errorMessage,
    int? completenessScore,
  }) {
    return ProfileState(
      profile: profile ?? this.profile,
      experiences: experiences ?? this.experiences,
      education: education ?? this.education,
      projects: projects ?? this.projects,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
      completenessScore: completenessScore ?? this.completenessScore,
    );
  }
}
```

### ProfileNotifier

**File**: `lib/providers/profile/profile_notifier.dart`

```dart
class ProfileNotifier extends StateNotifier<ProfileState> {
  final ProfilesApiClient _apiClient;

  ProfileNotifier(this._apiClient) : super(ProfileState.initial());

  Future<void> fetchProfile() async {
    state = state.copyWith(isLoading: true);

    try {
      final profile = await _apiClient.getMyProfile();
      final experiences = await _apiClient.getExperiences(profile.id);
      final education = await _apiClient.getEducation(profile.id);
      final projects = await _apiClient.getProjects(profile.id);
      final analytics = await _apiClient.getAnalytics(profile.id);

      state = state.copyWith(
        profile: profile,
        experiences: experiences,
        education: education,
        projects: projects,
        completenessScore: analytics['completeness_score'],
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  Future<void> updateProfile(Profile profile) async {
    try {
      final updated = await _apiClient.updateProfile(profile);
      state = state.copyWith(profile: updated);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> addExperience(Experience experience) async {
    try {
      final added = await _apiClient.addExperience(
        state.profile!.id,
        experience,
      );
      state = state.copyWith(
        experiences: [...state.experiences, added],
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<void> deleteExperience(String experienceId) async {
    try {
      await _apiClient.deleteExperiences(
        state.profile!.id,
        [experienceId],
      );
      state = state.copyWith(
        experiences: state.experiences
            .where((e) => e.id != experienceId)
            .toList(),
      );
    } catch (e) {
      rethrow;
    }
  }

  // Similar methods for education, projects, skills...
}

// Provider
final profileNotifierProvider = StateNotifierProvider<ProfileNotifier, ProfileState>(
  (ref) {
    final apiClient = ref.watch(profilesApiClientProvider);
    return ProfileNotifier(apiClient);
  },
);
```

---

## Service Layer

### ProfilesApiClient

**File**: `lib/services/api/profiles_api_client.dart`

```dart
class ProfilesApiClient {
  final Dio _dio;

  ProfilesApiClient(this._dio);

  Future<Profile> getMyProfile() async {
    try {
      final response = await _dio.get('/api/v1/profiles/me');
      return Profile.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Profile> createProfile(Profile profile) async {
    try {
      final response = await _dio.post(
        '/api/v1/profiles',
        data: profile.toJson(),
      );
      return Profile.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Profile> updateProfile(Profile profile) async {
    try {
      final response = await _dio.put(
        '/api/v1/profiles/${profile.id}',
        data: profile.toJson(),
      );
      return Profile.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<Experience>> getExperiences(String profileId) async {
    try {
      final response = await _dio.get('/api/v1/profiles/$profileId/experiences');
      return (response.data as List)
          .map((e) => Experience.fromJson(e))
          .toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Experience> addExperience(String profileId, Experience experience) async {
    try {
      final response = await _dio.post(
        '/api/v1/profiles/$profileId/experiences',
        data: {'experience': experience.toJson()},
      );
      return Experience.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> deleteExperiences(String profileId, List<String> ids) async {
    try {
      await _dio.delete(
        '/api/v1/profiles/$profileId/experiences',
        data: {'experience_ids': ids},
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getAnalytics(String profileId) async {
    try {
      final response = await _dio.get('/api/v1/profiles/$profileId/analytics');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // Education methods
  Future<List<Education>> getEducation(String profileId) async { ... }
  Future<Education> addEducation(String profileId, Education education) async { ... }
  Future<void> deleteEducation(String profileId, List<String> ids) async { ... }

  // Project methods
  Future<List<Project>> getProjects(String profileId) async { ... }
  Future<Project> addProject(String profileId, Project project) async { ... }
  Future<void> deleteProjects(String profileId, List<String> ids) async { ... }

  // Skills methods
  Future<Skills> getSkills(String profileId) async { ... }
  Future<void> updateSkills(String profileId, Skills skills) async { ... }
  Future<void> addTechnicalSkills(String profileId, List<String> skills) async { ... }
  Future<void> removeTechnicalSkills(String profileId, List<String> skills) async { ... }

  Exception _handleError(DioException error) {
    if (error.response != null) {
      final message = error.response?.data['detail'] ?? 'An error occurred';
      return Exception(message);
    }
    return Exception('Network error occurred');
  }
}

// Provider
final profilesApiClientProvider = Provider<ProfilesApiClient>((ref) {
  final dio = ref.watch(dioProvider);
  return ProfilesApiClient(dio);
});
```

---

## UI Components

### Profile Completeness Indicator

**File**: `lib/widgets/profile_completeness_indicator.dart`

```dart
class ProfileCompletenessIndicator extends StatelessWidget {
  final int score;

  const ProfileCompletenessIndicator({required this.score});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        CircularPercentIndicator(
          radius: 60.0,
          lineWidth: 8.0,
          percent: score / 100,
          center: Text(
            '$score%',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          progressColor: _getColor(score),
        ),
        SizedBox(height: 8),
        Text(_getMessage(score)),
      ],
    );
  }

  Color _getColor(int score) {
    if (score >= 80) return Colors.green;
    if (score >= 50) return Colors.orange;
    return Colors.red;
  }

  String _getMessage(int score) {
    if (score >= 80) return 'Great profile!';
    if (score >= 50) return 'Good progress';
    return 'Let\'s complete your profile';
  }
}
```

### Experience Card

**File**: `lib/widgets/experience_card.dart`

```dart
class ExperienceCard extends StatelessWidget {
  final Experience experience;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  const ExperienceCard({
    required this.experience,
    this.onEdit,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ExpansionTile(
        title: Text(experience.title),
        subtitle: Text('${experience.company} • ${_formatDates()}'),
        children: [
          Padding(
            padding: EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(experience.description),
                SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  children: experience.technologies
                      .map((tech) => Chip(label: Text(tech)))
                      .toList(),
                ),
                if (onEdit != null || onDelete != null)
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      if (onEdit != null)
                        TextButton(onPressed: onEdit, child: Text('Edit')),
                      if (onDelete != null)
                        TextButton(onPressed: onDelete, child: Text('Delete')),
                    ],
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatDates() {
    final start = DateFormat('MMM yyyy').format(experience.startDate);
    final end = experience.isCurrent
        ? 'Present'
        : DateFormat('MMM yyyy').format(experience.endDate!);
    return '$start - $end';
  }
}
```

---

## Testing

### Unit Tests

```dart
test('ProfileNotifier fetches profile successfully', () async {
  final mockClient = MockProfilesApiClient();
  final notifier = ProfileNotifier(mockClient);

  when(mockClient.getMyProfile()).thenAnswer((_) async => testProfile);
  when(mockClient.getExperiences(any)).thenAnswer((_) async => []);

  await notifier.fetchProfile();

  expect(notifier.state.profile, isNotNull);
  expect(notifier.state.isLoading, false);
});
```

### Widget Tests

```dart
testWidgets('ProfileViewScreen shows completeness indicator', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        profileNotifierProvider.overrideWith((ref) => mockNotifier),
      ],
      child: MaterialApp(home: ProfileViewScreen()),
    ),
  );

  expect(find.byType(ProfileCompletenessIndicator), findsOneWidget);
  expect(find.text('85%'), findsOneWidget);
});
```

---

## Performance Considerations

1. **Lazy Loading**: Load experiences/education/projects only when user expands sections
2. **Caching**: Cache profile data to avoid unnecessary API calls
3. **Debouncing**: Debounce skill additions when typing
4. **Optimistic Updates**: Update UI immediately, rollback on error

---

**Status**: ✅ Fully Implemented
**Screens**: 3 (View, Edit, Settings)
**API Endpoints**: 24 endpoints
**Dependencies**: dio, flutter_riverpod, intl
**Last Updated**: November 2025
