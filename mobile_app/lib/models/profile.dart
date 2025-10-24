import 'package:freezed_annotation/freezed_annotation.dart';

part 'profile.freezed.dart';
part 'profile.g.dart';

class Profile {
  const Profile({
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
      version: json['version'] as int,
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
      'version': version,
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
    int? version,
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
      version: version ?? this.version,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Profile &&
        other.id == id &&
        other.userId == userId &&
        other.personalInfo == personalInfo &&
        other.professionalSummary == professionalSummary &&
        other.experiences == experiences &&
        other.education == education &&
        other.skills == skills &&
        other.projects == projects &&
        other.customFields == customFields &&
        other.version == version &&
        other.createdAt == createdAt &&
        other.updatedAt == updatedAt;
  }

  @override
  int get hashCode {
    return id.hashCode ^
        userId.hashCode ^
        personalInfo.hashCode ^
        professionalSummary.hashCode ^
        experiences.hashCode ^
        education.hashCode ^
        skills.hashCode ^
        projects.hashCode ^
        customFields.hashCode ^
        version.hashCode ^
        createdAt.hashCode ^
        updatedAt.hashCode;
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
    // ignore: invalid_annotation_target
    @JsonKey(name: 'employment_type') String? employmentType,
    String? industry,
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
    // ignore: invalid_annotation_target
    @JsonKey(name: 'is_current') @Default(false) bool isCurrent,
    double? gpa,
    @Default([]) List<String> honors,
    String? description,
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
    @JsonKey(name: 'repository_url') String? repositoryUrl,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'start_date') String? startDate,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'end_date') String? endDate,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'is_ongoing') @Default(false) bool isOngoing,
    @Default([]) List<String> highlights,
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