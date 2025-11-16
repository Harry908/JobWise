import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../models/profile.dart' as model;
import '../services/api/profiles_api_client.dart';
import 'auth_provider.dart';

part 'profile_provider.g.dart';

@riverpod
ProfilesApiClient profilesApiClient(Ref ref) {
  return ProfilesApiClient(ref.watch(baseHttpClientProvider));
}

@Riverpod(keepAlive: true)
class Profile extends _$Profile {
  ProfilesApiClient get _api => ref.read(profilesApiClientProvider);

  @override
  Future<model.Profile?> build() async {
    // Depend on authentication status
    final authState = ref.watch(authProvider);
    if (authState.valueOrNull == null) {
      return null;
    }

    // User is authenticated, try to fetch profile
    try {
      return await _api.getCurrentUserProfile();
    } on DioException catch (e) {
      // A 404 is common for new users, so we just return null.
      if (e.response?.statusCode == 404) {
        return null;
      }
      // Other errors will be rethrown by AsyncValue.guard
      rethrow;
    }
  }

  Future<void> createProfile(model.Profile profile) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      return _api.createProfile(profile);
    });
  }

  Future<void> updateProfile(model.Profile profile) async {
    final currentValue = state.value;
    if (currentValue == null) return;
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final profileId = currentValue.id;
      return _api.updateProfile(profileId, profile);
    });
  }

  Future<void> deleteProfile() async {
    final currentValue = state.value;
    if (currentValue == null) return;
    final profileId = currentValue.id;
    state = const AsyncValue.loading();
    await AsyncValue.guard(() => _api.deleteProfile(profileId));
    state = const AsyncValue.data(null);
  }

  // Bulk Experience Operations
  Future<void> addExperiences(List<model.Experience> experiences) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      final createdExperiences =
          await _api.addExperiences(originalProfile.id, experiences);
      final updatedProfile = originalProfile.copyWith(
        experiences: [...originalProfile.experiences, ...createdExperiences],
      );
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  Future<void> updateExperiences(List<model.Experience> experiences) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      await _api.updateExperiences(originalProfile.id, experiences);
      final updatedProfile =
          originalProfile.copyWith(experiences: experiences);
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  Future<void> deleteExperiences(List<String> experienceIds) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      await _api.deleteExperiences(originalProfile.id, experienceIds);
      final updatedExperiences = originalProfile.experiences
          .where((exp) => !experienceIds.contains(exp.id))
          .toList();
      final updatedProfile =
          originalProfile.copyWith(experiences: updatedExperiences);
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  // Bulk Education Operations
  Future<void> addEducation(List<model.Education> education) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      final createdEducation = await _api.addEducation(
        originalProfile.id,
        education,
      );
      final updatedProfile = originalProfile.copyWith(
        education: [...originalProfile.education, ...createdEducation],
      );
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  Future<void> updateEducation(List<model.Education> education) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      await _api.updateEducation(originalProfile.id, education);
      final updatedProfile = originalProfile.copyWith(education: education);
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  Future<void> deleteEducation(List<String> educationIds) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      await _api.deleteEducation(originalProfile.id, educationIds);
      final updatedEducation = originalProfile.education
          .where((edu) => !educationIds.contains(edu.id))
          .toList();
      final updatedProfile =
          originalProfile.copyWith(education: updatedEducation);
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  // Bulk Project Operations
  Future<void> addProjects(List<model.Project> projects) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      final createdProjects = await _api.addProjects(
        originalProfile.id,
        projects,
      );
      final updatedProfile = originalProfile.copyWith(
        projects: [...originalProfile.projects, ...createdProjects],
      );
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  Future<void> updateProjects(List<model.Project> projects) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      await _api.updateProjects(originalProfile.id, projects);
      final updatedProfile = originalProfile.copyWith(projects: projects);
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  Future<void> deleteProjects(List<String> projectIds) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      await _api.deleteProjects(originalProfile.id, projectIds);
      final updatedProjects = originalProfile.projects
          .where((proj) => !projectIds.contains(proj.id))
          .toList();
      final updatedProfile =
          originalProfile.copyWith(projects: updatedProjects);
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  // Skills Operations
  Future<void> updateSkills(model.Skills skills) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      await _api.updateSkills(originalProfile.id, skills);
      final updatedProfile = originalProfile.copyWith(skills: skills);
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  Future<void> addTechnicalSkills(List<String> skills) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      await _api.addTechnicalSkills(originalProfile.id, skills);
      final updatedSkills = originalProfile.skills.copyWith(
        technical: [...originalProfile.skills.technical, ...skills],
      );
      final updatedProfile = originalProfile.copyWith(skills: updatedSkills);
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  Future<void> removeTechnicalSkills(List<String> skills) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      await _api.removeTechnicalSkills(originalProfile.id, skills);
      final updatedTechnicalSkills = originalProfile.skills.technical
          .where((skill) => !skills.contains(skill))
          .toList();
      final updatedSkills = originalProfile.skills.copyWith(
        technical: updatedTechnicalSkills,
      );
      final updatedProfile = originalProfile.copyWith(skills: updatedSkills);
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  Future<void> addSoftSkills(List<String> skills) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      await _api.addSoftSkills(originalProfile.id, skills);
      final updatedSkills = originalProfile.skills.copyWith(
        soft: [...originalProfile.skills.soft, ...skills],
      );
      final updatedProfile = originalProfile.copyWith(skills: updatedSkills);
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  Future<void> removeSoftSkills(List<String> skills) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      await _api.removeSoftSkills(originalProfile.id, skills);
      final updatedSoftSkills = originalProfile.skills.soft
          .where((skill) => !skills.contains(skill))
          .toList();
      final updatedSkills = originalProfile.skills.copyWith(
        soft: updatedSoftSkills,
      );
      final updatedProfile = originalProfile.copyWith(skills: updatedSkills);
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  // Certification Operations
  Future<void> addCertifications(
      List<model.Certification> certifications) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      final createdCertifications = await _api.addCertifications(
        originalProfile.id,
        certifications,
      );
      final updatedSkills = originalProfile.skills.copyWith(
        certifications: [
          ...originalProfile.skills.certifications,
          ...createdCertifications
        ],
      );
      final updatedProfile = originalProfile.copyWith(skills: updatedSkills);
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  Future<void> updateCertifications(
      List<model.Certification> certifications) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      await _api.updateCertifications(originalProfile.id, certifications);
      final updatedSkills =
          originalProfile.skills.copyWith(certifications: certifications);
      final updatedProfile = originalProfile.copyWith(skills: updatedSkills);
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  Future<void> deleteCertifications(List<String> certificationIds) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      await _api.deleteCertifications(originalProfile.id, certificationIds);
      final updatedCertifications = originalProfile.skills.certifications
          .where((cert) => !certificationIds.contains(cert.id))
          .toList();
      final updatedSkills = originalProfile.skills.copyWith(
        certifications: updatedCertifications,
      );
      final updatedProfile = originalProfile.copyWith(skills: updatedSkills);
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  // Custom Fields Operations
  Future<void> updateCustomFields(Map<String, dynamic> fields) async {
    final originalProfile = state.value;
    if (originalProfile == null) return;

    state = const AsyncValue.loading();

    try {
      await _api.updateCustomFields(originalProfile.id, fields);
      final updatedProfile = originalProfile.copyWith(customFields: fields);
      state = AsyncValue.data(updatedProfile);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  Future<model.ProfileAnalytics> getProfileAnalytics() async {
    final currentValue = state.value;
    if (currentValue == null) {
      throw Exception('No profile available');
    }

    try {
      return await _api.getProfileAnalytics(currentValue.id);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }
}