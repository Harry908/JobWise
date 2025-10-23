# Profile Feature - Mobile Design Document

**Version**: 2.0  
**Feature**: Master Resume Profile Management  
**API Service**: Profile API  
**Status**: Updated to match Backend API v2.1  
**Last Updated**: October 23, 2025

---

## Feature Overview

### Purpose
Manage master resume profiles containing personal information, work experiences, education, skills, projects, certifications, and custom fields.

### Key Features
- Create/edit comprehensive profile with nested components
- Bulk operations for experiences, education, projects
- Granular skills management (add/remove individual skills)
- Profile completeness analytics and recommendations
- Custom fields support for extensibility
- Offline-first with sync capabilities
- Version control and conflict resolution
- Comprehensive validation and error handling

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
import 'package:freezed_annotation/freezed_annotation.dart';

part 'profile.freezed.dart';
part 'profile.g.dart';

@freezed
class Profile with _$Profile {
  const factory Profile({
    required String id,
    required String userId,
    required PersonalInfo personalInfo,
    String? professionalSummary,
    @Default([]) List<Experience> experiences,
    @Default([]) List<Education> education,
    required Skills skills,
    @Default([]) List<Project> projects,
    @Default([]) List<Certification> certifications,
    @Default({}) Map<String, dynamic> customFields,
    required int version,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _Profile;

  factory Profile.fromJson(Map<String, dynamic> json) => _$ProfileFromJson(json);
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
  
  final _personalInfoFormKey = GlobalKey<FormState>();
  final _experiencesFormKey = GlobalKey<FormState>();
  final _educationFormKey = GlobalKey<FormState>();
  final _skillsFormKey = GlobalKey<FormState>();

  // Controllers for personal info
  late TextEditingController _fullNameController;
  late TextEditingController _emailController;
  late TextEditingController _phoneController;
  late TextEditingController _locationController;
  late TextEditingController _linkedinController;
  late TextEditingController _githubController;
  late TextEditingController _websiteController;
  late TextEditingController _summaryController;

  // Lists for dynamic components
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
            content: _buildPersonalInfoForm(),
            isActive: _currentStep >= 0,
          ),
          Step(
            title: const Text('Experience'),
            content: _buildExperiencesForm(),
            isActive: _currentStep >= 1,
          ),
          Step(
            title: const Text('Education & Skills'),
            content: _buildEducationSkillsForm(),
            isActive: _currentStep >= 2,
          ),
          Step(
            title: const Text('Projects'),
            content: _buildProjectsForm(),
            isActive: _currentStep >= 3,
          ),
        ],
      ),
    );
  }

  Widget _buildPersonalInfoForm() {
    return Form(
      key: _personalInfoFormKey,
      child: Column(
        children: [
          TextFormField(
            controller: _fullNameController,
            decoration: const InputDecoration(labelText: 'Full Name*'),
            validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
          ),
          TextFormField(
            controller: _emailController,
            decoration: const InputDecoration(labelText: 'Email*'),
            validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
          ),
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
    final profile = Profile(
      id: ref.read(profileProvider).profile?.id ?? '',
      userId: ref.read(profileProvider).profile?.userId ?? '',
      personalInfo: PersonalInfo(
        fullName: _fullNameController.text,
        email: _emailController.text,
        phone: _phoneController.text.isEmpty ? null : _phoneController.text,
        location: _locationController.text.isEmpty ? null : _locationController.text,
        linkedin: _linkedinController.text.isEmpty ? null : _linkedinController.text,
        github: _githubController.text.isEmpty ? null : _githubController.text,
        website: _websiteController.text.isEmpty ? null : _websiteController.text,
      ),
      professionalSummary: _summaryController.text.isEmpty ? null : _summaryController.text,
      experiences: _experiences,
      education: _education,
      skills: Skills(
        technical: _technicalSkills,
        soft: _softSkills,
      ),
      projects: _projects,
      version: ref.read(profileProvider).profile?.version ?? 1,
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

## Dependencies

```yaml
dependencies:
  freezed_annotation: ^2.4.1
  json_annotation: ^4.8.1
  
dev_dependencies:
  build_runner: ^2.4.6
  freezed: ^2.4.6
  json_serializable: ^6.7.1
```

---

**Document Status**: Updated to match Backend API v2.1  
**Last Updated**: October 23, 2025  
**Changes**: Added comprehensive API endpoints, granular skills management, custom fields, analytics, and updated data models to match backend implementation
