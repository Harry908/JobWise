// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'profile.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$PersonalInfoImpl _$$PersonalInfoImplFromJson(Map<String, dynamic> json) =>
    _$PersonalInfoImpl(
      fullName: json['full_name'] as String,
      email: json['email'] as String,
      phone: json['phone'] as String?,
      location: json['location'] as String?,
      linkedin: json['linkedin'] as String?,
      github: json['github'] as String?,
      website: json['website'] as String?,
    );

Map<String, dynamic> _$$PersonalInfoImplToJson(_$PersonalInfoImpl instance) =>
    <String, dynamic>{
      'full_name': instance.fullName,
      'email': instance.email,
      'phone': instance.phone,
      'location': instance.location,
      'linkedin': instance.linkedin,
      'github': instance.github,
      'website': instance.website,
    };

_$ExperienceImpl _$$ExperienceImplFromJson(Map<String, dynamic> json) =>
    _$ExperienceImpl(
      id: json['id'] as String?,
      title: json['title'] as String,
      company: json['company'] as String,
      location: json['location'] as String?,
      startDate: json['start_date'] as String,
      endDate: json['end_date'] as String?,
      isCurrent: json['is_current'] as bool? ?? false,
      description: json['description'] as String?,
      achievements:
          (json['achievements'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$ExperienceImplToJson(_$ExperienceImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'company': instance.company,
      'location': instance.location,
      'start_date': instance.startDate,
      'end_date': instance.endDate,
      'is_current': instance.isCurrent,
      'description': instance.description,
      'achievements': instance.achievements,
    };

_$EducationImpl _$$EducationImplFromJson(Map<String, dynamic> json) =>
    _$EducationImpl(
      id: json['id'] as String?,
      institution: json['institution'] as String,
      degree: json['degree'] as String,
      fieldOfStudy: json['field_of_study'] as String,
      startDate: json['start_date'] as String,
      endDate: json['end_date'] as String?,
      gpa: (json['gpa'] as num?)?.toDouble(),
      honors:
          (json['honors'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$EducationImplToJson(_$EducationImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'institution': instance.institution,
      'degree': instance.degree,
      'field_of_study': instance.fieldOfStudy,
      'start_date': instance.startDate,
      'end_date': instance.endDate,
      'gpa': instance.gpa,
      'honors': instance.honors,
    };

_$SkillsImpl _$$SkillsImplFromJson(Map<String, dynamic> json) => _$SkillsImpl(
  technical:
      (json['technical'] as List<dynamic>?)?.map((e) => e as String).toList() ??
      const [],
  soft:
      (json['soft'] as List<dynamic>?)?.map((e) => e as String).toList() ??
      const [],
  languages:
      (json['languages'] as List<dynamic>?)
          ?.map((e) => Language.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  certifications:
      (json['certifications'] as List<dynamic>?)
          ?.map((e) => Certification.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
);

Map<String, dynamic> _$$SkillsImplToJson(_$SkillsImpl instance) =>
    <String, dynamic>{
      'technical': instance.technical,
      'soft': instance.soft,
      'languages': instance.languages,
      'certifications': instance.certifications,
    };

_$LanguageImpl _$$LanguageImplFromJson(Map<String, dynamic> json) =>
    _$LanguageImpl(
      name: json['name'] as String,
      proficiency: json['proficiency'] as String,
    );

Map<String, dynamic> _$$LanguageImplToJson(_$LanguageImpl instance) =>
    <String, dynamic>{
      'name': instance.name,
      'proficiency': instance.proficiency,
    };

_$CertificationImpl _$$CertificationImplFromJson(Map<String, dynamic> json) =>
    _$CertificationImpl(
      id: json['id'] as String?,
      name: json['name'] as String,
      issuer: json['issuer'] as String,
      dateObtained: json['date_obtained'] as String,
      expiryDate: json['expiry_date'] as String?,
      credentialId: json['credential_id'] as String?,
    );

Map<String, dynamic> _$$CertificationImplToJson(_$CertificationImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'issuer': instance.issuer,
      'date_obtained': instance.dateObtained,
      'expiry_date': instance.expiryDate,
      'credential_id': instance.credentialId,
    };

_$ProjectImpl _$$ProjectImplFromJson(Map<String, dynamic> json) =>
    _$ProjectImpl(
      id: json['id'] as String?,
      name: json['name'] as String,
      description: json['description'] as String,
      technologies:
          (json['technologies'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      url: json['url'] as String?,
      startDate: json['start_date'] as String?,
      endDate: json['end_date'] as String?,
    );

Map<String, dynamic> _$$ProjectImplToJson(_$ProjectImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'technologies': instance.technologies,
      'url': instance.url,
      'start_date': instance.startDate,
      'end_date': instance.endDate,
    };

_$ProfileAnalyticsImpl _$$ProfileAnalyticsImplFromJson(
  Map<String, dynamic> json,
) => _$ProfileAnalyticsImpl(
  profileId: json['profile_id'] as String,
  completeness: Map<String, int>.from(json['completeness'] as Map),
  statistics: json['statistics'] as Map<String, dynamic>,
  recommendations:
      (json['recommendations'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList() ??
      const [],
);

Map<String, dynamic> _$$ProfileAnalyticsImplToJson(
  _$ProfileAnalyticsImpl instance,
) => <String, dynamic>{
  'profile_id': instance.profileId,
  'completeness': instance.completeness,
  'statistics': instance.statistics,
  'recommendations': instance.recommendations,
};
