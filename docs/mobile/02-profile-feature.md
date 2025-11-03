# Profile Feature - Mobile Design Document

**Version**: 2.2
**Feature**: Master Resume Profile Management
**API Service**: Profile API
**Status**: ✅ **Sprint 1 Complete** (Core CRUD, bulk operations implemented)
**Last Updated**: November 2, 2025 - **Backend sync**: Education/Project date validations fixed

---

## Implementation Status

### ✅ Implemented Features
- **Minimal profile creation**: Create profile with just name and email
- Core profile CRUD (create, read, update, delete)
- Multi-step profile form (Personal Info, Experience, Education/Skills, Projects)
- All steps optional except Personal Info (name + email required)
- Work experience management with CRUD dialogs and date pickers
- Education management with CRUD dialogs and date pickers
- Technical and soft skills with tag-based input
- Project management with CRUD dialogs and date pickers
- Date format settings (US MM/dd/yyyy, European dd/MM/yyyy, ISO yyyy-MM-dd)
- Settings screen for date format configuration
- Profile API client with all endpoints
- Profile state management with Riverpod
- Navigation with proper back button support
- Comprehensive error handling

### ⚠️ Partially Implemented
- **Profile Analytics**: API client ready, no UI visualization
- **Custom Fields**: API client ready, no UI for management
- **Certifications**: Model and API ready, not in profile form
- **Languages**: Model exists, not in profile form

### ❌ Not Implemented
- Profile analytics display screen (API ready, UI pending)
- Custom fields management UI (API ready, UI pending)
- Certifications management UI (model + API ready, dialog missing)
- Languages management UI (model ready, no API or dialog)
- Offline profile editing with sync
- Minimal profile creation flow (backend supports name+email only, mobile forces 4-step form)

### ⚠️ Known Issues (Fixed in Backend v2.2)
- **RESOLVED**: Education `endDate` validation error - Backend now accepts optional endDate
- **RESOLVED**: Project `startDate` validation error - Backend now accepts optional startDate
- Education `isCurrent` field - Mobile has it, backend doesn't use it
- Project missing fields - `repository_url` and `highlights` not in mobile dialog

---

## Feature Overview

### Purpose
Manage master resume profiles containing personal information, work experiences, education, skills, projects, certifications, and custom fields.

### Key Features
- **Minimal profile creation**: Only personal info (name + email) and empty skills object required
- **Progressive enhancement**: Add experiences, education, projects, skills later
- Create/edit comprehensive profile with nested components
- Bulk operations for experiences, education, projects
- Granular skills management (add/remove individual skills)
- Profile completeness analytics and recommendations
- Custom fields support for extensibility
- Offline-first with sync capabilities
- Comprehensive validation and error handling

### Profile Creation Requirements

**Required for initial profile creation:**
- Personal Info: `full_name` and `email` (minimum)

**Completely optional (can be added/updated anytime):**
- Professional summary
- Work experiences
- Education entries
- Skills (technical, soft, languages, certifications)
- Projects
- Custom fields

**Progressive Profile Building**: Users can create a minimal profile with just name and email, then add or update any component at any time through the profile edit screen. The backend accepts partial updates, so users only need to send changed fields.

---

## Profile Creation Flow

### Minimum Viable Profile
Users can create a profile with just the essentials and progressively enhance it:

**Minimum Required Data:**
```json
{
  "personal_info": {
    "full_name": "John Doe",
    "email": "john@example.com"
  },
  "skills": {
    "technical": [],
    "soft": [],
    "languages": [],
    "certifications": []
  }
}
```

**Progressive Enhancement:**
1. **Step 1 (Required)**: Personal Info → Name and Email
2. **Step 2 (Optional)**: Add work experiences when ready
3. **Step 3 (Optional)**: Add education and skills when ready
4. **Step 4 (Optional)**: Add projects when ready

All steps except Step 1 can be skipped during initial profile creation. Users can add these details later via profile edit.

### Multi-Step Form Design
The profile form uses a stepper with optional steps:

- **Step 0: Personal Info** (Required) - Name, Email, Phone, Location, LinkedIn, GitHub, Website, Summary
- **Step 1: Experience** (Optional) - Add work experiences or skip
- **Step 2: Education & Skills** (Optional) - Add education entries and skills or skip
- **Step 3: Projects** (Optional) - Add projects or skip

**Navigation:**
- "Continue" button validates current step and moves to next
- "Skip" or continue with empty data on optional steps
- "Cancel" button returns to previous step
- Final step shows "Save Profile" button

---

## API Integration

### Backend Connection
```dart
// Base URL: http://10.0.2.2:8000/api/v1
// All endpoints require JWT authentication
```

### Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/profiles` | POST | Create profile with all components |
| `/profiles/me` | GET | Get current user's profile |
| `/profiles/{id}` | GET/PUT/DELETE | CRUD operations |
| `/profiles/{id}/analytics` | GET | Completeness metrics |
| `/profiles/{id}/experiences` | POST/PUT/DELETE | Bulk experience operations |
| `/profiles/{id}/experiences` | GET | List all experiences |
| `/profiles/{id}/education` | POST/PUT/DELETE | Bulk education operations |
| `/profiles/{id}/education` | GET | List all education |
| `/profiles/{id}/projects` | POST/PUT/DELETE | Bulk project operations |
| `/profiles/{id}/projects` | GET | List all projects |
| `/profiles/{id}/skills` | GET/PUT | Skills management |
| `/profiles/{id}/skills/technical` | POST/PUT | Add/update technical skills |
| `/profiles/{id}/skills/soft` | POST/PUT | Add/update soft skills |
| `/profiles/{id}/custom-fields` | GET/PUT | Custom fields management |

---

## Data Models

### Profile Model
```dart
// lib/models/profile.dart
// NOTE: Manual implementation (not using freezed)
// REQUIRED FIELDS: Only personal_info (with full_name + email) and skills (can be empty)
// ALL OTHER FIELDS ARE OPTIONAL and can be added later

class Profile {
  const Profile({
    required this.id,
    required this.userId,
    required this.personalInfo,  // REQUIRED: must have full_name and email
    this.professionalSummary,    // OPTIONAL
    this.experiences = const [], // OPTIONAL: can be empty list
    this.education = const [],   // OPTIONAL: can be empty list
    required this.skills,        // REQUIRED: but can be empty Skills()
    this.projects = const [],    // OPTIONAL: can be empty list
    this.customFields = const {}, // OPTIONAL: can be empty map
    required this.createdAt,
    required this.updatedAt,
  });
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

  factory Profile.fromJson(Map<String, dynamic> json) {
    // Convert user_id to string if it's an integer
    final userId = json['user_id'] is int
        ? json['user_id'].toString()
        : json['user_id'] as String;

    return Profile(
      id: json['id'] as String,
      userId: userId,
      personalInfo: PersonalInfo.fromJson(json['personal_info'] as Map<String, dynamic>),
      professionalSummary: json['professional_summary'] as String?,
      experiences: (json['experiences'] as List<dynamic>?)
          ?.map((e) => Experience.fromJson(e as Map<String, dynamic>))
          .toList() ?? const [],
      education: (json['education'] as List<dynamic>?)
          ?.map((e) => Education.fromJson(e as Map<String, dynamic>))
          .toList() ?? const [],
      skills: Skills.fromJson(json['skills'] as Map<String, dynamic>),
      projects: (json['projects'] as List<dynamic>?)
          ?.map((e) => Project.fromJson(e as Map<String, dynamic>))
          .toList() ?? const [],
      customFields: (json['custom_fields'] as Map<String, dynamic>?) ?? const {},
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'personal_info': personalInfo.toJson(),
      'professional_summary': professionalSummary,
      'experiences': experiences.map((e) => e.toJson()).toList(),
      'education': education.map((e) => e.toJson()).toList(),
      'skills': skills.toJson(),
      'projects': projects.map((e) => e.toJson()).toList(),
      'custom_fields': customFields,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  Profile copyWith({
    String? id,
    String? userId,
    PersonalInfo? personalInfo,
    String? professionalSummary,
    List<Experience>? experiences,
    List<Education>? education,
    Skills? skills,
    List<Project>? projects,
    Map<String, dynamic>? customFields,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Profile(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      personalInfo: personalInfo ?? this.personalInfo,
      professionalSummary: professionalSummary ?? this.professionalSummary,
      experiences: experiences ?? this.experiences,
      education: education ?? this.education,
      skills: skills ?? this.skills,
      projects: projects ?? this.projects,
      customFields: customFields ?? this.customFields,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

@freezed
class PersonalInfo with _$PersonalInfo {
  const factory PersonalInfo({
    required String fullName,
    required String email,
    String? phone,
    String? location,
    String? linkedin,
    String? github,
    String? website,
    String? portfolioUrl,
    String? headline,
  }) = _PersonalInfo;

  factory PersonalInfo.fromJson(Map<String, dynamic> json) => 
      _$PersonalInfoFromJson(json);
}

@freezed
class Experience with _$Experience {
  const factory Experience({
    String? id,
    required String title,
    required String company,
    String? location,
    required String startDate,
    String? endDate,
    @Default(false) bool isCurrent,
    String? description,
    @Default([]) List<String> achievements,
    String? employmentType,
    String? industry,
  }) = _Experience;

  factory Experience.fromJson(Map<String, dynamic> json) => 
      _$ExperienceFromJson(json);
}

@freezed
class Education with _$Education {
  const factory Education({
    String? id,
    required String institution,
    required String degree,
    required String fieldOfStudy,
    required String startDate,
    String? endDate,
    @Default(false) bool isCurrent,
    double? gpa,
    @Default([]) List<String> honors,
    String? description,
  }) = _Education;

  factory Education.fromJson(Map<String, dynamic> json) => 
      _$EducationFromJson(json);
}

@freezed
class Skills with _$Skills {
  const factory Skills({
    @Default([]) List<String> technical,
    @Default([]) List<String> soft,
    @Default([]) List<Language> languages,
    @Default([]) List<Certification> certifications,
  }) = _Skills;

  factory Skills.fromJson(Map<String, dynamic> json) => 
      _$SkillsFromJson(json);
}

@freezed
class Language with _$Language {
  const factory Language({
    required String name,
    required String proficiency, // native, fluent, conversational, basic
  }) = _Language;

  factory Language.fromJson(Map<String, dynamic> json) => 
      _$LanguageFromJson(json);
}

@freezed
class Certification with _$Certification {
  const factory Certification({
    String? id,
    required String name,
    required String issuer,
    required String dateObtained,
    String? expiryDate,
    String? credentialId,
  }) = _Certification;

  factory Certification.fromJson(Map<String, dynamic> json) => 
      _$CertificationFromJson(json);
}

@freezed
class Project with _$Project {
  const factory Project({
    String? id,
    required String name,
    required String description,
    @Default([]) List<String> technologies,
    String? url,
    String? repositoryUrl,
    String? startDate,
    String? endDate,
    @Default(false) bool isOngoing,
    @Default([]) List<String> highlights,
  }) = _Project;

  factory Project.fromJson(Map<String, dynamic> json) => 
      _$ProjectFromJson(json);
}
```

---

## State Management

```dart
// lib/providers/profile_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import '../models/profile.dart';
import '../services/api/profiles_api_client.dart';

part 'profile_provider.freezed.dart';

@freezed
class ProfileState with _$ProfileState {
  const factory ProfileState({
    Profile? profile,
    @Default(false) bool isLoading,
    @Default(false) bool isSaving,
    String? errorMessage,
  }) = _ProfileState;
}

class ProfileNotifier extends StateNotifier<ProfileState> {
  final ProfilesApiClient _profileApi;

  ProfileNotifier(this._profileApi) : super(const ProfileState()) {
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    state = state.copyWith(isLoading: true);
    try {
      final profile = await _profileApi.getCurrentUserProfile();
      state = state.copyWith(profile: profile, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false);
      // No profile exists yet (404 is expected)
    }
  }

  Future<void> createProfile(Profile profile) async {
    state = state.copyWith(isSaving: true, errorMessage: null);
    try {
      final createdProfile = await _profileApi.createProfile(profile);
      state = state.copyWith(profile: createdProfile, isSaving: false);
    } catch (e) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'Failed to create profile',
      );
      rethrow;
    }
  }

  Future<void> updateProfile(Profile profile) async {
    state = state.copyWith(isSaving: true, errorMessage: null);
    try {
      final updatedProfile = await _profileApi.updateProfile(
        state.profile!.id,
        profile,
      );
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'Failed to update profile',
      );
      rethrow;
    }
  }

  Future<void> addExperiences(List<Experience> experiences) async {
    if (state.profile == null) return;
    state = state.copyWith(isSaving: true);
    try {
      final createdExperiences = await _profileApi.addExperiences(
        state.profile!.id,
        experiences,
      );
      final updatedProfile = state.profile!.copyWith(
        experiences: [...state.profile!.experiences, ...createdExperiences],
      );
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.toString());
      rethrow;
    }
  }

  Future<void> updateExperiences(List<Experience> experiences) async {
    if (state.profile == null) return;
    state = state.copyWith(isSaving: true);
    try {
      await _profileApi.updateExperiences(state.profile!.id, experiences);
      final updatedProfile = state.profile!.copyWith(experiences: experiences);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      state = state.copyWith(isSaving: false);
      rethrow;
    }
  }

  // Similar methods for education, projects, skills
  Future<void> getProfileAnalytics() async {
    if (state.profile == null) return;
    state = state.copyWith(isLoading: true);
    try {
      final analytics = await _profileApi.getProfileAnalytics(state.profile!.id);
      // Update state with analytics data
      state = state.copyWith(isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.toString());
    }
  }

  Future<List<Experience>> getExperiences() async {
    if (state.profile == null) return [];
    try {
      return await _profileApi.getExperiences(state.profile!.id);
    } catch (e) {
      state = state.copyWith(errorMessage: e.toString());
      return [];
    }
  }

  Future<List<Education>> getEducation() async {
    if (state.profile == null) return [];
    try {
      return await _profileApi.getEducation(state.profile!.id);
    } catch (e) {
      state = state.copyWith(errorMessage: e.toString());
      return [];
    }
  }

  Future<List<Project>> getProjects() async {
    if (state.profile == null) return [];
    try {
      return await _profileApi.getProjects(state.profile!.id);
    } catch (e) {
      state = state.copyWith(errorMessage: e.toString());
      return [];
    }
  }

  Future<Skills> getSkills() async {
    if (state.profile == null) return const Skills();
    try {
      return await _profileApi.getSkills(state.profile!.id);
    } catch (e) {
      state = state.copyWith(errorMessage: e.toString());
      return const Skills();
    }
  }

  Future<void> addTechnicalSkills(List<String> skills) async {
    if (state.profile == null) return;
    state = state.copyWith(isSaving: true);
    try {
      await _profileApi.addTechnicalSkills(state.profile!.id, skills);
      // Refresh skills
      final updatedSkills = await _profileApi.getSkills(state.profile!.id);
      final updatedProfile = state.profile!.copyWith(skills: updatedSkills);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.toString());
      rethrow;
    }
  }

  Future<void> addSoftSkills(List<String> skills) async {
    if (state.profile == null) return;
    state = state.copyWith(isSaving: true);
    try {
      await _profileApi.addSoftSkills(state.profile!.id, skills);
      // Refresh skills
      final updatedSkills = await _profileApi.getSkills(state.profile!.id);
      final updatedProfile = state.profile!.copyWith(skills: updatedSkills);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.toString());
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getCustomFields() async {
    if (state.profile == null) return {};
    try {
      return await _profileApi.getCustomFields(state.profile!.id);
    } catch (e) {
      state = state.copyWith(errorMessage: e.toString());
      return {};
    }
  }

  Future<void> updateCustomFields(Map<String, dynamic> customFields) async {
    if (state.profile == null) return;
    state = state.copyWith(isSaving: true);
    try {
      await _profileApi.updateCustomFields(state.profile!.id, customFields);
      final updatedProfile = state.profile!.copyWith(customFields: customFields);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.toString());
      rethrow;
    }
  }
}

final profileProvider = StateNotifierProvider<ProfileNotifier, ProfileState>((ref) {
  return ProfileNotifier(ref.watch(profilesApiClientProvider));
});
```

---

## Service Layer

```dart
// lib/services/api/profiles_api_client.dart
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/profile.dart';
import 'base_http_client.dart';

class ProfilesApiClient {
  final BaseHttpClient _client;

  ProfilesApiClient(this._client);

  Future<Profile> createProfile(Profile profile) async {
    final response = await _client.post('/profiles', data: profile.toJson());
    return Profile.fromJson(response.data);
  }

  Future<Profile> getCurrentUserProfile() async {
    final response = await _client.get('/profiles/me');
    return Profile.fromJson(response.data);
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

  // Bulk operations
  Future<List<Experience>> addExperiences(
    String profileId,
    List<Experience> experiences,
  ) async {
    final response = await _client.post(
      '/profiles/$profileId/experiences',
      data: experiences.map((e) => e.toJson()).toList(),
    );
    return (response.data as List)
        .map((json) => Experience.fromJson(json))
        .toList();
  }

  Future<List<Experience>> updateExperiences(
    String profileId,
    List<Experience> experiences,
  ) async {
    final response = await _client.put(
      '/profiles/$profileId/experiences',
      data: experiences.map((e) => e.toJson()).toList(),
    );
    return (response.data as List)
        .map((json) => Experience.fromJson(json))
        .toList();
  }

  Future<void> deleteExperiences(String profileId, List<String> ids) async {
    await _client.delete(
      '/profiles/$profileId/experiences',
      data: {'experience_ids': ids},
    );
  }

  // Similar methods for education, projects, certifications
  Future<Map<String, dynamic>> getProfileAnalytics(String profileId) async {
    final response = await _client.get('/profiles/$profileId/analytics');
    return response.data;
  }

  Future<List<Experience>> getExperiences(String profileId) async {
    final response = await _client.get('/profiles/$profileId/experiences');
    return (response.data['experiences'] as List)
        .map((json) => Experience.fromJson(json))
        .toList();
  }

  Future<List<Education>> getEducation(String profileId) async {
    final response = await _client.get('/profiles/$profileId/education');
    return (response.data['education'] as List)
        .map((json) => Education.fromJson(json))
        .toList();
  }

  Future<List<Project>> getProjects(String profileId) async {
    final response = await _client.get('/profiles/$profileId/projects');
    return (response.data['projects'] as List)
        .map((json) => Project.fromJson(json))
        .toList();
  }

  Future<Skills> getSkills(String profileId) async {
    final response = await _client.get('/profiles/$profileId/skills');
    return Skills.fromJson(response.data);
  }

  Future<void> addTechnicalSkills(String profileId, List<String> skills) async {
    await _client.post('/profiles/$profileId/skills/technical', data: skills);
  }

  Future<void> addSoftSkills(String profileId, List<String> skills) async {
    await _client.post('/profiles/$profileId/skills/soft', data: skills);
  }

  Future<Map<String, dynamic>> getCustomFields(String profileId) async {
    final response = await _client.get('/profiles/$profileId/custom-fields');
    return response.data;
  }

  Future<void> updateCustomFields(String profileId, Map<String, dynamic> customFields) async {
    await _client.put('/profiles/$profileId/custom-fields', data: customFields);
  }
}

final profilesApiClientProvider = Provider<ProfilesApiClient>((ref) {
  return ProfilesApiClient(ref.watch(baseHttpClientProvider));
});
```

---

## UI Components

### Profile Form Screen (Multi-step)

**Design Philosophy:**
- Only Step 0 (Personal Info) is required with name and email
- Steps 1-3 (Experience, Education/Skills, Projects) are fully optional
- Users can create a minimal profile and enhance it later
- No validation on optional steps - empty lists are acceptable

```dart
// lib/screens/profile_edit_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ProfileEditScreen extends ConsumerStatefulWidget {
  const ProfileEditScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<ProfileEditScreen> createState() => _ProfileEditScreenState();
}

class _ProfileEditScreenState extends ConsumerState<ProfileEditScreen> {
  int _currentStep = 0;
  
  final _formKey = GlobalKey<FormState>();  // Only for Step 0 validation

  // Controllers for REQUIRED fields (Step 0)
  late TextEditingController _fullNameController;
  late TextEditingController _emailController;
  
  // Controllers for OPTIONAL fields
  late TextEditingController _phoneController;
  late TextEditingController _locationController;
  late TextEditingController _linkedinController;
  late TextEditingController _githubController;
  late TextEditingController _websiteController;
  late TextEditingController _summaryController;

  // Lists for dynamic components (ALL OPTIONAL - can be empty)
  List<Experience> _experiences = [];
  List<Education> _education = [];
  List<String> _technicalSkills = [];
  List<String> _softSkills = [];
  List<Project> _projects = [];

  @override
  void initState() {
    super.initState();
    _initializeControllers();
    _loadExistingProfile();
  }

  void _initializeControllers() {
    _fullNameController = TextEditingController();
    _emailController = TextEditingController();
    _phoneController = TextEditingController();
    _locationController = TextEditingController();
    _linkedinController = TextEditingController();
    _githubController = TextEditingController();
    _websiteController = TextEditingController();
    _summaryController = TextEditingController();
  }

  void _loadExistingProfile() {
    final profile = ref.read(profileProvider).profile;
    if (profile != null) {
      _fullNameController.text = profile.personalInfo.fullName;
      _emailController.text = profile.personalInfo.email;
      _phoneController.text = profile.personalInfo.phone ?? '';
      _locationController.text = profile.personalInfo.location ?? '';
      _linkedinController.text = profile.personalInfo.linkedin ?? '';
      _githubController.text = profile.personalInfo.github ?? '';
      _websiteController.text = profile.personalInfo.website ?? '';
      _summaryController.text = profile.professionalSummary ?? '';
      _experiences = List.from(profile.experiences);
      _education = List.from(profile.education);
      _technicalSkills = List.from(profile.skills.technical);
      _softSkills = List.from(profile.skills.soft);
      _projects = List.from(profile.projects);
    }
  }

  @override
  Widget build(BuildContext context) {
    final profileState = ref.watch(profileProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Edit Profile'),
      ),
      body: Stepper(
        currentStep: _currentStep,
        onStepContinue: _onStepContinue,
        onStepCancel: _onStepCancel,
        controlsBuilder: (context, details) {
          return Row(
            children: [
              if (_currentStep < 3)
                ElevatedButton(
                  onPressed: details.onStepContinue,
                  child: const Text('Continue'),
                ),
              if (_currentStep == 3)
                ElevatedButton(
                  onPressed: profileState.isSaving ? null : _saveProfile,
                  child: profileState.isSaving
                      ? const CircularProgressIndicator()
                      : const Text('Save Profile'),
                ),
              const SizedBox(width: 8),
              if (_currentStep > 0)
                TextButton(
                  onPressed: details.onStepCancel,
                  child: const Text('Back'),
                ),
            ],
          );
        },
        steps: [
          Step(
            title: const Text('Personal Info'),
            subtitle: const Text('Required'),
            content: _buildPersonalInfoForm(),
            isActive: _currentStep >= 0,
            state: _getStepState(0),
          ),
          Step(
            title: const Text('Experience'),
            subtitle: const Text('Optional - Skip if not ready'),
            content: _buildExperiencesForm(),
            isActive: _currentStep >= 1,
            state: _getStepState(1),
          ),
          Step(
            title: const Text('Education & Skills'),
            subtitle: const Text('Optional - Skip if not ready'),
            content: _buildEducationSkillsForm(),
            isActive: _currentStep >= 2,
            state: _getStepState(2),
          ),
          Step(
            title: const Text('Projects'),
            subtitle: const Text('Optional - Skip if not ready'),
            content: _buildProjectsForm(),
            isActive: _currentStep >= 3,
            state: _getStepState(3),
          ),
        ],
      ),
    );
  }

  Widget _buildPersonalInfoForm() {
    return Form(
      key: _formKey,  // Only form that requires validation
      child: Column(
        children: [
          // REQUIRED FIELDS
          TextFormField(
            controller: _fullNameController,
            decoration: const InputDecoration(
              labelText: 'Full Name*',
              hintText: 'John Doe',
            ),
            validator: (v) => v?.trim().isEmpty ?? true ? 'Full name is required' : null,
          ),
          TextFormField(
            controller: _emailController,
            decoration: const InputDecoration(
              labelText: 'Email*',
              hintText: 'john@example.com',
            ),
            keyboardType: TextInputType.emailAddress,
            validator: (v) {
              if (v?.trim().isEmpty ?? true) return 'Email is required';
              if (!v!.contains('@')) return 'Invalid email format';
              return null;
            },
          ),
          const SizedBox(height: 16),
          const Divider(),
          const Text(
            'Optional Information',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          // OPTIONAL FIELDS - No validation required
          TextFormField(
            controller: _phoneController,
            decoration: const InputDecoration(labelText: 'Phone'),
          ),
          TextFormField(
            controller: _locationController,
            decoration: const InputDecoration(labelText: 'Location'),
          ),
          TextFormField(
            controller: _linkedinController,
            decoration: const InputDecoration(labelText: 'LinkedIn URL'),
          ),
          TextFormField(
            controller: _githubController,
            decoration: const InputDecoration(labelText: 'GitHub URL'),
          ),
          TextFormField(
            controller: _summaryController,
            decoration: const InputDecoration(labelText: 'Professional Summary'),
            maxLines: 4,
          ),
        ],
      ),
    );
  }

  Widget _buildExperiencesForm() {
    return Column(
      children: [
        ..._experiences.asMap().entries.map((entry) {
          return ExperienceCard(
            experience: entry.value,
            onEdit: () => _editExperience(entry.key),
            onDelete: () => _deleteExperience(entry.key),
          );
        }).toList(),
        ElevatedButton.icon(
          onPressed: _addExperience,
          icon: const Icon(Icons.add),
          label: const Text('Add Experience'),
        ),
      ],
    );
  }

  Widget _buildEducationSkillsForm() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Education', style: TextStyle(fontWeight: FontWeight.bold)),
        ..._education.map((edu) => EducationCard(
              education: edu,
              onEdit: () {},
              onDelete: () {},
            )),
        ElevatedButton.icon(
          onPressed: _addEducation,
          icon: const Icon(Icons.add),
          label: const Text('Add Education'),
        ),
        const SizedBox(height: 24),
        const Text('Skills', style: TextStyle(fontWeight: FontWeight.bold)),
        Wrap(
          spacing: 8,
          children: _technicalSkills
              .map((skill) => Chip(
                    label: Text(skill),
                    onDeleted: () {
                      setState(() {
                        _technicalSkills.remove(skill);
                      });
                    },
                  ))
              .toList(),
        ),
        TextField(
          decoration: const InputDecoration(
            labelText: 'Add Technical Skill',
            suffixIcon: Icon(Icons.add),
          ),
          onSubmitted: (value) {
            if (value.isNotEmpty) {
              setState(() {
                _technicalSkills.add(value);
              });
            }
          },
        ),
      ],
    );
  }

  Widget _buildProjectsForm() {
    return Column(
      children: [
        ..._projects.map((project) => ProjectCard(
              project: project,
              onEdit: () {},
              onDelete: () {},
            )),
        ElevatedButton.icon(
          onPressed: _addProject,
          icon: const Icon(Icons.add),
          label: const Text('Add Project'),
        ),
      ],
    );
  }

  void _onStepContinue() {
    // Only validate Step 0 (Personal Info) - it's the only required step
    if (_currentStep == 0) {
      if (!_formKey.currentState!.validate()) {
        // Show error: name and email are required
        return;
      }
    }
    // Steps 1-3 are optional - no validation needed
    // Users can continue with empty experiences/education/projects/skills
    
    if (_currentStep < 3) {
      setState(() {
        _currentStep++;
      });
    }
  }

  void _onStepCancel() {
    if (_currentStep > 0) {
      setState(() {
        _currentStep--;
      });
    }
  }

  Future<void> _saveProfile() async {
    // Validate required fields one more time before saving
    if (!_formKey.currentState!.validate()) {
      setState(() => _currentStep = 0);  // Go back to Step 0
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill in required fields (Name and Email)')),
      );
      return;
    }
    
    final profile = Profile(
      id: ref.read(profileProvider).profile?.id ?? '',
      userId: ref.read(profileProvider).profile?.userId ?? '',
      personalInfo: PersonalInfo(
        fullName: _fullNameController.text.trim(),
        email: _emailController.text.trim(),
        // Optional fields
        phone: _phoneController.text.isEmpty ? null : _phoneController.text.trim(),
        location: _locationController.text.isEmpty ? null : _locationController.text.trim(),
        linkedin: _linkedinController.text.isEmpty ? null : _linkedinController.text.trim(),
        github: _githubController.text.isEmpty ? null : _githubController.text.trim(),
        website: _websiteController.text.isEmpty ? null : _websiteController.text.trim(),
      ),
      professionalSummary: _summaryController.text.isEmpty ? null : _summaryController.text.trim(),
      // These can all be empty lists - totally fine!
      experiences: _experiences,
      education: _education,
      skills: Skills(
        technical: _technicalSkills,  // Can be empty []
        soft: _softSkills,            // Can be empty []
        languages: [],                 // Can be empty []
        certifications: [],            // Can be empty []
      ),
      projects: _projects,             // Can be empty []
      customFields: {},                // Can be empty {}
      createdAt: ref.read(profileProvider).profile?.createdAt ?? DateTime.now(),
      updatedAt: DateTime.now(),
    );

    try {
      if (ref.read(profileProvider).profile == null) {
        await ref.read(profileProvider.notifier).createProfile(profile);
      } else {
        await ref.read(profileProvider.notifier).updateProfile(profile);
      }
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Profile saved successfully')),
      );
      Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }

  void _addExperience() {
    // Show dialog to add experience
  }

  void _editExperience(int index) {
    // Show dialog to edit experience
  }

  void _deleteExperience(int index) {
    setState(() {
      _experiences.removeAt(index);
    });
  }

  void _addEducation() {
    // Show dialog
  }

  void _addProject() {
    // Show dialog
  }

  @override
  void dispose() {
    _fullNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _locationController.dispose();
    _linkedinController.dispose();
    _githubController.dispose();
    _websiteController.dispose();
    _summaryController.dispose();
    super.dispose();
  }
}
```

---

### Testing Strategy

### Unit Tests
- Test ProfileNotifier state transitions for all operations
- Test ProfilesApiClient HTTP requests for all endpoints
- Test model serialization/deserialization with all fields
- Test bulk operations and error handling

### Widget Tests
- Test profile form validation with comprehensive fields
- Test adding/removing experiences, education, projects
- Test skills management (add/remove individual skills)
- Test stepper navigation and form flow
- Test analytics display and recommendations

### Integration Tests
- Test full profile creation flow with all components
- Test bulk operations (add multiple experiences/education/projects)
- Test granular skills management
- Test custom fields operations
- Test profile analytics and completeness scoring
- Test offline editing with sync

---

## Implementation Checklist

- [x] Create Profile, PersonalInfo, Experience, Education, Skills, Project models (manual implementation)
- [x] Remove version field from Profile model (per requirements)
- [x] **Implement minimal profile creation** (only name + email required)
- [x] **Mark optional steps clearly** in multi-step form UI
- [x] **Validate only Step 0** (Personal Info) - all other steps optional
- [x] Implement ProfilesApiClient with all CRUD endpoints
- [x] Implement bulk operations for experiences, education, projects
- [x] Implement granular skills management (add/remove)
- [x] Implement custom fields operations
- [x] Create ProfileNotifier with Riverpod
- [x] Build multi-step ProfileEditScreen UI (Personal Info, Experience, Education/Skills, Projects)
- [x] Create ExperienceDialog, EducationDialog, ProjectDialog widgets
- [x] Implement tag-based input for skills (TagInput widget)
- [x] Add date pickers for all date fields
- [x] Implement date format system (US/European/ISO)
- [x] Create SettingsScreen for date format configuration
- [x] Fix navigation back buttons (context.push)
- [x] Add comprehensive error handling
- [x] Test profile creation flow with minimal data
- [x] Test profile creation flow with complete data
- [ ] Add unit tests for ProfilesApiClient
- [ ] Add unit tests for ProfileNotifier
- [ ] Add widget tests for ProfileEditScreen
- [ ] Add integration tests for minimal profile creation
- [ ] Add integration tests for progressive profile enhancement
- [ ] Build ProfileAnalyticsScreen UI (API ready, UI pending)
- [ ] Build CustomFieldsScreen UI (API ready, UI pending)
- [ ] Add Certifications to profile form (model and API ready)
- [ ] Add Languages to profile form (model ready)
- [ ] Implement offline profile editing with sync
- [ ] Test on physical Android device
- [ ] Test on iOS simulator

---

## Dependencies

```yaml
dependencies:
  flutter_riverpod: ^2.6.1
  dio: ^5.7.0
  intl: ^0.18.1
  
# Note: No longer using freezed - models are manually implemented
```

---

## Backend Sync Status (v2.2 - November 2, 2025)

### ✅ Fixed Validation Issues
1. **Education `endDate`**: Backend now accepts optional endDate (previously required)
2. **Project `startDate`**: Backend now accepts optional startDate (previously required)
3. **Profile Creation**: Backend now properly saves experiences/education/projects on create

### Remaining Discrepancies
1. **Minimal Profile Flow**: Backend supports name+email only, mobile requires 4-step form
2. **Certifications**: Mobile has model + API client methods but no UI dialog
3. **Languages**: Mobile has model but no UI or API endpoints
4. **Custom Fields**: API ready but no mobile UI for management
5. **Analytics**: API endpoint exists but no mobile visualization screen
6. **Project Fields**: Backend supports `repository_url` and `highlights`, mobile dialog missing them

**Document Status**: ✅ Sprint 1 Complete - Backend sync issues resolved
**Last Updated**: November 2, 2025
**Changes**:
- **Backend validation fixed**: Education endDate and Project startDate now optional in backend
- **Documented missing features**: Certifications, Languages, Custom Fields, Analytics UI
- **Noted discrepancies**: Mobile enforces 4-step form vs backend minimal profile support
- Updated implementation status to reflect Sprint 1 completion
- Removed version field from Profile model
- Changed from freezed to manual implementation
- Added date format system (US/European/ISO)

**Backend Validation (Verified Working):**
- ✅ Profile creation with only `personal_info` (name + email) and empty `skills` object works
- ✅ All other fields (`experiences`, `education`, `projects`, `professional_summary`) are optional
- ✅ Empty lists for experiences/education/projects are valid
- ✅ Empty skills lists (technical, soft, languages, certifications) are valid
- ✅ Education without endDate now validated successfully
- ✅ Projects without startDate now validated successfully
