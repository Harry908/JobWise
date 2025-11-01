import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/profile.dart';
import '../services/api/profiles_api_client.dart';
import 'auth_provider.dart';

class ProfileState {
  final Profile? profile;
  final bool isLoading;
  final bool isSaving;
  final String? errorMessage;

  const ProfileState({
    this.profile,
    this.isLoading = false,
    this.isSaving = false,
    this.errorMessage,
  });

  factory ProfileState.initial() => const ProfileState();

  ProfileState copyWith({
    Profile? profile,
    bool? isLoading,
    bool? isSaving,
    String? errorMessage,
  }) {
    return ProfileState(
      profile: profile ?? this.profile,
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

class ProfileNotifier extends StateNotifier<ProfileState> {
  final ProfilesApiClient _profileApi;

  ProfileNotifier(this._profileApi) : super(ProfileState.initial()) {
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    state = state.copyWith(isLoading: true);
    try {
      final profile = await _profileApi.getCurrentUserProfile();
      state = state.copyWith(profile: profile, isLoading: false);
    } catch (e) {
      // No profile exists yet (404 is expected for new users)
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> refreshProfile() async {
    await _loadProfile();
  }

  Future<void> createProfile(Profile profile) async {
    state = state.copyWith(isSaving: true, errorMessage: null);
    try {
      print('ProfileNotifier: Creating profile with ${profile.experiences.length} experiences');
      final createdProfile = await _profileApi.createProfile(profile);
      print('ProfileNotifier: Profile created successfully with ${createdProfile.experiences.length} experiences');
      state = state.copyWith(profile: createdProfile, isSaving: false);
    } on DioException catch (e) {
      print('ProfileNotifier: DioException during profile creation: ${e.response?.data}');
      final errorMessage = _extractErrorMessage(e, 'Failed to create profile');
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    } catch (e) {
      print('ProfileNotifier: Unexpected error during profile creation: $e');
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'An unexpected error occurred while creating profile',
      );
      rethrow;
    }
  }

  Future<void> updateProfile(Profile profile) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true, errorMessage: null);
    try {
      print('ProfileNotifier: Updating profile with ${profile.experiences.length} experiences');
      final updatedProfile = await _profileApi.updateProfile(
        state.profile!.id,
        profile,
      );
      print('ProfileNotifier: Profile updated successfully with ${updatedProfile.experiences.length} experiences');
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } on DioException catch (e) {
      print('ProfileNotifier: DioException during profile update: ${e.response?.data}');
      final errorMessage = _extractErrorMessage(e, 'Failed to update profile');
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    } catch (e) {
      print('ProfileNotifier: Unexpected error during profile update: $e');
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'An unexpected error occurred while updating profile',
      );
      rethrow;
    }
  }

  Future<void> deleteProfile() async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true, errorMessage: null);
    try {
      await _profileApi.deleteProfile(state.profile!.id);
      state = ProfileState.initial();
    } on DioException catch (e) {
      final errorMessage = _extractErrorMessage(e, 'Failed to delete profile');
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    } catch (e) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'An unexpected error occurred while deleting profile',
      );
      rethrow;
    }
  }

  // Helper method to extract user-friendly error messages from DioException
  String _extractErrorMessage(DioException error, String defaultMessage) {
    if (error.response?.data is Map) {
      final data = error.response!.data as Map<String, dynamic>;
      if (data.containsKey('detail')) {
        return data['detail'] as String;
      }
      if (data.containsKey('message')) {
        return data['message'] as String;
      }
    }
    if (error.response?.statusMessage != null) {
      return error.response!.statusMessage!;
    }
    return '$defaultMessage. Please try again.';
  }

  // Bulk Experience Operations
  Future<void> addExperiences(List<Experience> experiences) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true, errorMessage: null);
    try {
      final createdExperiences = await _profileApi.addExperiences(
        state.profile!.id,
        experiences,
      );
      final updatedProfile = state.profile!.copyWith(
        experiences: [...state.profile!.experiences, ...createdExperiences],
      );
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } on DioException catch (e) {
      final errorMessage = _extractErrorMessage(e, 'Failed to add experiences');
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    } catch (e) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'An unexpected error occurred while adding experiences',
      );
      rethrow;
    }
  }

  Future<void> updateExperiences(List<Experience> experiences) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true, errorMessage: null);
    try {
      await _profileApi.updateExperiences(state.profile!.id, experiences);
      final updatedProfile = state.profile!.copyWith(experiences: experiences);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } on DioException catch (e) {
      final errorMessage = _extractErrorMessage(e, 'Failed to update experiences');
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    } catch (e) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'An unexpected error occurred while updating experiences',
      );
      rethrow;
    }
  }

  Future<void> deleteExperiences(List<String> experienceIds) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true, errorMessage: null);
    try {
      await _profileApi.deleteExperiences(state.profile!.id, experienceIds);
      final updatedExperiences = state.profile!.experiences
          .where((exp) => !experienceIds.contains(exp.id))
          .toList();
      final updatedProfile = state.profile!.copyWith(experiences: updatedExperiences);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } on DioException catch (e) {
      final errorMessage = _extractErrorMessage(e, 'Failed to delete experiences');
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    } catch (e) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'An unexpected error occurred while deleting experiences',
      );
      rethrow;
    }
  }

  // Bulk Education Operations
  Future<void> addEducation(List<Education> education) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true);
    try {
      final createdEducation = await _profileApi.addEducation(
        state.profile!.id,
        education,
      );
      final updatedProfile = state.profile!.copyWith(
        education: [...state.profile!.education, ...createdEducation],
      );
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      String errorMessage = 'Failed to add education. Please try again.';
      if (e is String) {
        errorMessage = e;
      }
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    }
  }

  Future<void> updateEducation(List<Education> education) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true);
    try {
      await _profileApi.updateEducation(state.profile!.id, education);
      final updatedProfile = state.profile!.copyWith(education: education);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      String errorMessage = 'Failed to update education. Please try again.';
      if (e is String) {
        errorMessage = e;
      }
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    }
  }

  Future<void> deleteEducation(List<String> educationIds) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true);
    try {
      await _profileApi.deleteEducation(state.profile!.id, educationIds);
      final updatedEducation = state.profile!.education
          .where((edu) => !educationIds.contains(edu.id))
          .toList();
      final updatedProfile = state.profile!.copyWith(education: updatedEducation);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      String errorMessage = 'Failed to delete education. Please try again.';
      if (e is String) {
        errorMessage = e;
      }
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    }
  }

  // Bulk Project Operations
  Future<void> addProjects(List<Project> projects) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true);
    try {
      final createdProjects = await _profileApi.addProjects(
        state.profile!.id,
        projects,
      );
      final updatedProfile = state.profile!.copyWith(
        projects: [...state.profile!.projects, ...createdProjects],
      );
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      String errorMessage = 'Failed to add projects. Please try again.';
      if (e is String) {
        errorMessage = e;
      }
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    }
  }

  Future<void> updateProjects(List<Project> projects) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true);
    try {
      await _profileApi.updateProjects(state.profile!.id, projects);
      final updatedProfile = state.profile!.copyWith(projects: projects);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      String errorMessage = 'Failed to update projects. Please try again.';
      if (e is String) {
        errorMessage = e;
      }
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    }
  }

  Future<void> deleteProjects(List<String> projectIds) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true);
    try {
      await _profileApi.deleteProjects(state.profile!.id, projectIds);
      final updatedProjects = state.profile!.projects
          .where((proj) => !projectIds.contains(proj.id))
          .toList();
      final updatedProfile = state.profile!.copyWith(projects: updatedProjects);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      String errorMessage = 'Failed to delete projects. Please try again.';
      if (e is String) {
        errorMessage = e;
      }
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    }
  }

  // Skills Operations
  Future<void> updateSkills(Skills skills) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true);
    try {
      await _profileApi.updateSkills(state.profile!.id, skills);
      final updatedProfile = state.profile!.copyWith(skills: skills);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      String errorMessage = 'Failed to update skills. Please try again.';
      if (e is String) {
        errorMessage = e;
      }
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    }
  }

  Future<void> addTechnicalSkills(List<String> skills) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true);
    try {
      await _profileApi.addTechnicalSkills(state.profile!.id, skills);
      final updatedSkills = state.profile!.skills.copyWith(
        technical: [...state.profile!.skills.technical, ...skills],
      );
      final updatedProfile = state.profile!.copyWith(skills: updatedSkills);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      String errorMessage = 'Failed to add technical skills. Please try again.';
      if (e is String) {
        errorMessage = e;
      }
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    }
  }

  Future<void> removeTechnicalSkills(List<String> skills) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true);
    try {
      await _profileApi.removeTechnicalSkills(state.profile!.id, skills);
      final updatedTechnicalSkills = state.profile!.skills.technical
          .where((skill) => !skills.contains(skill))
          .toList();
      final updatedSkills = state.profile!.skills.copyWith(
        technical: updatedTechnicalSkills,
      );
      final updatedProfile = state.profile!.copyWith(skills: updatedSkills);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      String errorMessage = 'Failed to remove technical skills. Please try again.';
      if (e is String) {
        errorMessage = e;
      }
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    }
  }

  Future<void> addSoftSkills(List<String> skills) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true);
    try {
      await _profileApi.addSoftSkills(state.profile!.id, skills);
      final updatedSkills = state.profile!.skills.copyWith(
        soft: [...state.profile!.skills.soft, ...skills],
      );
      final updatedProfile = state.profile!.copyWith(skills: updatedSkills);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      String errorMessage = 'Failed to add soft skills. Please try again.';
      if (e is String) {
        errorMessage = e;
      }
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    }
  }

  Future<void> removeSoftSkills(List<String> skills) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true);
    try {
      await _profileApi.removeSoftSkills(state.profile!.id, skills);
      final updatedSoftSkills = state.profile!.skills.soft
          .where((skill) => !skills.contains(skill))
          .toList();
      final updatedSkills = state.profile!.skills.copyWith(
        soft: updatedSoftSkills,
      );
      final updatedProfile = state.profile!.copyWith(skills: updatedSkills);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      String errorMessage = 'Failed to remove soft skills. Please try again.';
      if (e is String) {
        errorMessage = e;
      }
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    }
  }

  // Certification Operations
  Future<void> addCertifications(List<Certification> certifications) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true);
    try {
      final createdCertifications = await _profileApi.addCertifications(
        state.profile!.id,
        certifications,
      );
      final updatedSkills = state.profile!.skills.copyWith(
        certifications: [...state.profile!.skills.certifications, ...createdCertifications],
      );
      final updatedProfile = state.profile!.copyWith(skills: updatedSkills);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      String errorMessage = 'Failed to add certifications. Please try again.';
      if (e is String) {
        errorMessage = e;
      }
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    }
  }

  Future<void> updateCertifications(List<Certification> certifications) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true);
    try {
      await _profileApi.updateCertifications(state.profile!.id, certifications);
      final updatedSkills = state.profile!.skills.copyWith(certifications: certifications);
      final updatedProfile = state.profile!.copyWith(skills: updatedSkills);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      String errorMessage = 'Failed to update certifications. Please try again.';
      if (e is String) {
        errorMessage = e;
      }
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    }
  }

  Future<void> deleteCertifications(List<String> certificationIds) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true);
    try {
      await _profileApi.deleteCertifications(state.profile!.id, certificationIds);
      final updatedCertifications = state.profile!.skills.certifications
          .where((cert) => !certificationIds.contains(cert.id))
          .toList();
      final updatedSkills = state.profile!.skills.copyWith(
        certifications: updatedCertifications,
      );
      final updatedProfile = state.profile!.copyWith(skills: updatedSkills);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      String errorMessage = 'Failed to delete certifications. Please try again.';
      if (e is String) {
        errorMessage = e;
      }
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    }
  }

  // Custom Fields Operations
  Future<void> updateCustomFields(Map<String, dynamic> fields) async {
    if (state.profile == null) return;

    state = state.copyWith(isSaving: true);
    try {
      await _profileApi.updateCustomFields(state.profile!.id, fields);
      final updatedProfile = state.profile!.copyWith(customFields: fields);
      state = state.copyWith(profile: updatedProfile, isSaving: false);
    } catch (e) {
      String errorMessage = 'Failed to update custom fields. Please try again.';
      if (e is String) {
        errorMessage = e;
      }
      state = state.copyWith(
        isSaving: false,
        errorMessage: errorMessage,
      );
      rethrow;
    }
  }

  Future<ProfileAnalytics> getProfileAnalytics() async {
    if (state.profile == null) {
      throw Exception('No profile available');
    }

    try {
      return await _profileApi.getProfileAnalytics(state.profile!.id);
    } catch (e) {
      String errorMessage = 'Failed to load profile analytics.';
      if (e is DioException && e.error is String) {
        errorMessage = e.error as String;
      }
      state = state.copyWith(errorMessage: errorMessage);
      rethrow;
    }
  }
}

// Providers
final profilesApiClientProvider = Provider<ProfilesApiClient>((ref) {
  return ProfilesApiClient(ref.watch(baseHttpClientProvider));
});

final profileProvider = StateNotifierProvider<ProfileNotifier, ProfileState>((ref) {
  return ProfileNotifier(ref.watch(profilesApiClientProvider));
});