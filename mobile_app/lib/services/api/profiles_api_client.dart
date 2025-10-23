import '../../models/profile.dart';
import 'base_http_client.dart';

class ProfilesApiClient {
  final BaseHttpClient _client;

  ProfilesApiClient(this._client);

  // Profile CRUD Operations
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

  Future<ProfileAnalytics> getProfileAnalytics(String id) async {
    final response = await _client.get('/profiles/$id/analytics');
    return ProfileAnalytics.fromJson(response.data);
  }

  // Bulk Experience Operations
  Future<List<Experience>> addExperiences(String profileId, List<Experience> experiences) async {
    final response = await _client.post(
      '/profiles/$profileId/experiences',
      data: experiences.map((e) => e.toJson()).toList(),
    );
    return (response.data as List)
        .map((json) => Experience.fromJson(json))
        .toList();
  }

  Future<List<Experience>> updateExperiences(String profileId, List<Experience> experiences) async {
    final response = await _client.put(
      '/profiles/$profileId/experiences',
      data: experiences.map((e) => e.toJson()).toList(),
    );
    return (response.data as List)
        .map((json) => Experience.fromJson(json))
        .toList();
  }

  Future<void> deleteExperiences(String profileId, List<String> experienceIds) async {
    await _client.delete(
      '/profiles/$profileId/experiences',
      data: {'experience_ids': experienceIds},
    );
  }

  Future<List<Experience>> getExperiences(String profileId, {int? limit, int? offset}) async {
    final queryParams = <String, dynamic>{};
    if (limit != null) queryParams['limit'] = limit;
    if (offset != null) queryParams['offset'] = offset;

    final response = await _client.get(
      '/profiles/$profileId/experiences',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
    );
    return (response.data['experiences'] as List)
        .map((json) => Experience.fromJson(json))
        .toList();
  }

  // Bulk Education Operations
  Future<List<Education>> addEducation(String profileId, List<Education> education) async {
    final response = await _client.post(
      '/profiles/$profileId/education',
      data: education.map((e) => e.toJson()).toList(),
    );
    return (response.data as List)
        .map((json) => Education.fromJson(json))
        .toList();
  }

  Future<List<Education>> updateEducation(String profileId, List<Education> education) async {
    final response = await _client.put(
      '/profiles/$profileId/education',
      data: education.map((e) => e.toJson()).toList(),
    );
    return (response.data as List)
        .map((json) => Education.fromJson(json))
        .toList();
  }

  Future<void> deleteEducation(String profileId, List<String> educationIds) async {
    await _client.delete(
      '/profiles/$profileId/education',
      data: {'education_ids': educationIds},
    );
  }

  // Bulk Project Operations
  Future<List<Project>> addProjects(String profileId, List<Project> projects) async {
    final response = await _client.post(
      '/profiles/$profileId/projects',
      data: projects.map((p) => p.toJson()).toList(),
    );
    return (response.data as List)
        .map((json) => Project.fromJson(json))
        .toList();
  }

  Future<List<Project>> updateProjects(String profileId, List<Project> projects) async {
    final response = await _client.put(
      '/profiles/$profileId/projects',
      data: projects.map((p) => p.toJson()).toList(),
    );
    return (response.data as List)
        .map((json) => Project.fromJson(json))
        .toList();
  }

  Future<void> deleteProjects(String profileId, List<String> projectIds) async {
    await _client.delete(
      '/profiles/$profileId/projects',
      data: {'project_ids': projectIds},
    );
  }

  // Skills Operations
  Future<Skills> getSkills(String profileId) async {
    final response = await _client.get('/profiles/$profileId/skills');
    return Skills.fromJson(response.data);
  }

  Future<Skills> updateSkills(String profileId, Skills skills) async {
    final response = await _client.put('/profiles/$profileId/skills', data: skills.toJson());
    return Skills.fromJson(response.data);
  }

  Future<void> addTechnicalSkills(String profileId, List<String> skills) async {
    await _client.post(
      '/profiles/$profileId/skills/technical',
      data: {'skills': skills},
    );
  }

  Future<void> removeTechnicalSkills(String profileId, List<String> skills) async {
    await _client.delete(
      '/profiles/$profileId/skills/technical',
      data: {'skills': skills},
    );
  }

  Future<void> addSoftSkills(String profileId, List<String> skills) async {
    await _client.post(
      '/profiles/$profileId/skills/soft',
      data: {'skills': skills},
    );
  }

  Future<void> removeSoftSkills(String profileId, List<String> skills) async {
    await _client.delete(
      '/profiles/$profileId/skills/soft',
      data: {'skills': skills},
    );
  }

  // Certification Operations
  Future<List<Certification>> addCertifications(String profileId, List<Certification> certifications) async {
    final response = await _client.post(
      '/profiles/$profileId/certifications',
      data: certifications.map((c) => c.toJson()).toList(),
    );
    return (response.data as List)
        .map((json) => Certification.fromJson(json))
        .toList();
  }

  Future<List<Certification>> updateCertifications(String profileId, List<Certification> certifications) async {
    final response = await _client.put(
      '/profiles/$profileId/certifications',
      data: certifications.map((c) => c.toJson()).toList(),
    );
    return (response.data as List)
        .map((json) => Certification.fromJson(json))
        .toList();
  }

  Future<void> deleteCertifications(String profileId, List<String> certificationIds) async {
    await _client.delete(
      '/profiles/$profileId/certifications',
      data: {'certification_ids': certificationIds},
    );
  }

  // Custom Fields Operations
  Future<Map<String, dynamic>> getCustomFields(String profileId) async {
    final response = await _client.get('/profiles/$profileId/custom-fields');
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> updateCustomFields(String profileId, Map<String, dynamic> fields) async {
    final response = await _client.put(
      '/profiles/$profileId/custom-fields',
      data: {'fields': fields.entries.map((e) => {'key': e.key, 'value': e.value}).toList()},
    );
    return response.data as Map<String, dynamic>;
  }
}