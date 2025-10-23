import 'package:freezed_annotation/freezed_annotation.dart';

part 'profile.freezed.dart';
part 'profile.g.dart';

@freezed
class Profile with _$Profile {
  const factory Profile({
    required String id,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'user_id') required String userId,
    required PersonalInfo personalInfo,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'professional_summary') String? professionalSummary,
    @Default([]) List<Experience> experiences,
    @Default([]) List<Education> education,
    required Skills skills,
    @Default([]) List<Project> projects,
    @Default({}) Map<String, dynamic> customFields,
    required int version,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'created_at') required DateTime createdAt,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'updated_at') required DateTime updatedAt,
  }) = _Profile;

  factory Profile.fromJson(Map<String, dynamic> json) {
    // Convert user_id to string if it's an integer
    if (json['user_id'] is int) {
      json = Map<String, dynamic>.from(json)..['user_id'] = json['user_id'].toString();
    }
    return _$ProfileFromJson(json);
  }
}

@freezed
class PersonalInfo with _$PersonalInfo {
  const factory PersonalInfo({
    // ignore: invalid_annotation_target
    @JsonKey(name: 'full_name') required String fullName,
    required String email,
    String? phone,
    String? location,
    String? linkedin,
    String? github,
    String? website,
  }) = _PersonalInfo;

  factory PersonalInfo.fromJson(Map<String, dynamic> json) => _$PersonalInfoFromJson(json);
}

@freezed
class Experience with _$Experience {
  const factory Experience({
    String? id,
    required String title,
    required String company,
    String? location,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'start_date') required String startDate,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'end_date') String? endDate,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'is_current') @Default(false) bool isCurrent,
    String? description,
    @Default([]) List<String> achievements,
  }) = _Experience;

  factory Experience.fromJson(Map<String, dynamic> json) => _$ExperienceFromJson(json);
}

@freezed
class Education with _$Education {
  const factory Education({
    String? id,
    required String institution,
    required String degree,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'field_of_study') required String fieldOfStudy,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'start_date') required String startDate,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'end_date') String? endDate,
    double? gpa,
    @Default([]) List<String> honors,
  }) = _Education;

  factory Education.fromJson(Map<String, dynamic> json) => _$EducationFromJson(json);
}

@freezed
class Skills with _$Skills {
  const factory Skills({
    @Default([]) List<String> technical,
    @Default([]) List<String> soft,
    @Default([]) List<Language> languages,
    @Default([]) List<Certification> certifications,
  }) = _Skills;

  factory Skills.fromJson(Map<String, dynamic> json) => _$SkillsFromJson(json);
}

@freezed
class Language with _$Language {
  const factory Language({
    required String name,
    required String proficiency, // native, fluent, conversational, basic
  }) = _Language;

  factory Language.fromJson(Map<String, dynamic> json) => _$LanguageFromJson(json);
}

@freezed
class Certification with _$Certification {
  const factory Certification({
    String? id,
    required String name,
    required String issuer,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'date_obtained') required String dateObtained,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'expiry_date') String? expiryDate,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'credential_id') String? credentialId,
  }) = _Certification;

  factory Certification.fromJson(Map<String, dynamic> json) => _$CertificationFromJson(json);
}

@freezed
class Project with _$Project {
  const factory Project({
    String? id,
    required String name,
    required String description,
    @Default([]) List<String> technologies,
    String? url,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'start_date') String? startDate,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'end_date') String? endDate,
  }) = _Project;

  factory Project.fromJson(Map<String, dynamic> json) => _$ProjectFromJson(json);
}

@freezed
class ProfileAnalytics with _$ProfileAnalytics {
  const factory ProfileAnalytics({
    // ignore: invalid_annotation_target
    @JsonKey(name: 'profile_id') required String profileId,
    required Map<String, int> completeness,
    required Map<String, dynamic> statistics,
    @Default([]) List<String> recommendations,
  }) = _ProfileAnalytics;

  factory ProfileAnalytics.fromJson(Map<String, dynamic> json) => _$ProfileAnalyticsFromJson(json);
}