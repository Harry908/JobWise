// Manual implementation for Profile class
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

class PersonalInfo {
  const PersonalInfo({
    required this.fullName,
    required this.email,
    this.phone,
    this.location,
    this.linkedin,
    this.github,
    this.website,
  });

  final String fullName;
  final String email;
  final String? phone;
  final String? location;
  final String? linkedin;
  final String? github;
  final String? website;

  factory PersonalInfo.fromJson(Map<String, dynamic> json) {
    return PersonalInfo(
      fullName: json['full_name'] as String,
      email: json['email'] as String,
      phone: json['phone'] as String?,
      location: json['location'] as String?,
      linkedin: json['linkedin'] as String?,
      github: json['github'] as String?,
      website: json['website'] as String?,
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

class Experience {
  const Experience({
    this.id,
    required this.title,
    required this.company,
    this.location,
    required this.startDate,
    this.endDate,
    this.isCurrent = false,
    this.description,
    this.achievements = const [],
    this.employmentType,
    this.industry,
  });

  final String? id;
  final String title;
  final String company;
  final String? location;
  final String startDate;
  final String? endDate;
  final bool isCurrent;
  final String? description;
  final List<String> achievements;
  final String? employmentType;
  final String? industry;

  factory Experience.fromJson(Map<String, dynamic> json) {
    return Experience(
      id: json['id'] as String?,
      title: json['title'] as String,
      company: json['company'] as String,
      location: json['location'] as String?,
      startDate: json['start_date'] as String,
      endDate: json['end_date'] as String?,
      isCurrent: json['is_current'] as bool? ?? false,
      description: json['description'] as String?,
      achievements: (json['achievements'] as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      employmentType: json['employment_type'] as String?,
      industry: json['industry'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'company': company,
      'location': location,
      'start_date': startDate,
      'end_date': endDate,
      'is_current': isCurrent,
      'description': description,
      'achievements': achievements,
      'employment_type': employmentType,
      'industry': industry,
    };
  }
}

class Education {
  const Education({
    this.id,
    required this.institution,
    required this.degree,
    required this.fieldOfStudy,
    required this.startDate,
    this.endDate,
    this.isCurrent = false,
    this.gpa,
    this.honors = const [],
    this.description,
  });

  final String? id;
  final String institution;
  final String degree;
  final String fieldOfStudy;
  final String startDate;
  final String? endDate;
  final bool isCurrent;
  final double? gpa;
  final List<String> honors;
  final String? description;

  factory Education.fromJson(Map<String, dynamic> json) {
    return Education(
      id: json['id'] as String?,
      institution: json['institution'] as String,
      degree: json['degree'] as String,
      fieldOfStudy: json['field_of_study'] as String,
      startDate: json['start_date'] as String,
      endDate: json['end_date'] as String?,
      isCurrent: json['is_current'] as bool? ?? false,
      gpa: (json['gpa'] as num?)?.toDouble(),
      honors: (json['honors'] as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      description: json['description'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'institution': institution,
      'degree': degree,
      'field_of_study': fieldOfStudy,
      'start_date': startDate,
      'end_date': endDate,
      'is_current': isCurrent,
      'gpa': gpa,
      'honors': honors,
      'description': description,
    };
  }
}

class Skills {
  const Skills({
    this.technical = const [],
    this.soft = const [],
    this.languages = const [],
    this.certifications = const [],
  });

  final List<String> technical;
  final List<String> soft;
  final List<Language> languages;
  final List<Certification> certifications;

  factory Skills.fromJson(Map<String, dynamic> json) {
    return Skills(
      technical: (json['technical'] as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      soft: (json['soft'] as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      languages: (json['languages'] as List<dynamic>?)?.map((e) => Language.fromJson(e as Map<String, dynamic>)).toList() ?? const [],
      certifications: (json['certifications'] as List<dynamic>?)?.map((e) => Certification.fromJson(e as Map<String, dynamic>)).toList() ?? const [],
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

  Skills copyWith({
    List<String>? technical,
    List<String>? soft,
    List<Language>? languages,
    List<Certification>? certifications,
  }) {
    return Skills(
      technical: technical ?? this.technical,
      soft: soft ?? this.soft,
      languages: languages ?? this.languages,
      certifications: certifications ?? this.certifications,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Skills &&
        other.technical == technical &&
        other.soft == soft &&
        other.languages == languages &&
        other.certifications == certifications;
  }

  @override
  int get hashCode {
    return technical.hashCode ^
        soft.hashCode ^
        languages.hashCode ^
        certifications.hashCode;
  }
}

class Language {
  const Language({
    required this.name,
    required this.proficiency,
  });

  final String name;
  final String proficiency;

  factory Language.fromJson(Map<String, dynamic> json) {
    return Language(
      name: json['name'] as String,
      proficiency: json['proficiency'] as String,
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
  const Certification({
    this.id,
    required this.name,
    required this.issuer,
    required this.dateObtained,
    this.expiryDate,
    this.credentialId,
  });

  final String? id;
  final String name;
  final String issuer;
  final String dateObtained;
  final String? expiryDate;
  final String? credentialId;

  factory Certification.fromJson(Map<String, dynamic> json) {
    return Certification(
      id: json['id'] as String?,
      name: json['name'] as String,
      issuer: json['issuer'] as String,
      dateObtained: json['date_obtained'] as String,
      expiryDate: json['expiry_date'] as String?,
      credentialId: json['credential_id'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'issuer': issuer,
      'date_obtained': dateObtained,
      'expiry_date': expiryDate,
      'credential_id': credentialId,
    };
  }
}

class Project {
  const Project({
    this.id,
    required this.name,
    required this.description,
    this.technologies = const [],
    this.url,
    this.repositoryUrl,
    this.startDate,
    this.endDate,
    this.isOngoing = false,
    this.highlights = const [],
  });

  final String? id;
  final String name;
  final String description;
  final List<String> technologies;
  final String? url;
  final String? repositoryUrl;
  final String? startDate;
  final String? endDate;
  final bool isOngoing;
  final List<String> highlights;

  factory Project.fromJson(Map<String, dynamic> json) {
    return Project(
      id: json['id'] as String?,
      name: json['name'] as String,
      description: json['description'] as String,
      technologies: (json['technologies'] as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      url: json['url'] as String?,
      repositoryUrl: json['repository_url'] as String?,
      startDate: json['start_date'] as String?,
      endDate: json['end_date'] as String?,
      isOngoing: json['is_ongoing'] as bool? ?? false,
      highlights: (json['highlights'] as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'technologies': technologies,
      'url': url,
      'repository_url': repositoryUrl,
      'start_date': startDate,
      'end_date': endDate,
      'is_ongoing': isOngoing,
      'highlights': highlights,
    };
  }
}

class ProfileAnalytics {
  const ProfileAnalytics({
    required this.profileId,
    required this.completeness,
    required this.statistics,
    this.recommendations = const [],
  });

  final String profileId;
  final Map<String, int> completeness;
  final Map<String, dynamic> statistics;
  final List<String> recommendations;

  factory ProfileAnalytics.fromJson(Map<String, dynamic> json) {
    return ProfileAnalytics(
      profileId: json['profile_id'] as String,
      completeness: Map<String, int>.from(json['completeness'] as Map),
      statistics: json['statistics'] as Map<String, dynamic>,
      recommendations: (json['recommendations'] as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'profile_id': profileId,
      'completeness': completeness,
      'statistics': statistics,
      'recommendations': recommendations,
    };
  }
}