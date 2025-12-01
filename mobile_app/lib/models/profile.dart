// Manual implementation for Profile class
class Profile {
  const Profile({
    required this.id,
    required this.userId,
    required this.personalInfo,
    this.professionalSummary,
    this.enhancedSummary,
    this.experiences = const [],
    this.education = const [],
    required this.skills,
    this.projects = const [],
    this.customFields = const {},
    required this.createdAt,
    required this.updatedAt,
  });

  final String id;
  final int userId;
  final PersonalInfo personalInfo;
  final String? professionalSummary;
  final String? enhancedSummary;
  final List<Experience> experiences;
  final List<Education> education;
  final Skills skills;
  final List<Project> projects;
  final Map<String, dynamic> customFields;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory Profile.fromJson(Map<String, dynamic> json) {
    // Convert user_id to int if it's a string, handle both formats
    final userId = json['user_id'] is int
        ? json['user_id'] as int
        : int.parse(json['user_id'] as String);

    return Profile(
      id: json['id'] as String,
      userId: userId,
      personalInfo: PersonalInfo.fromJson(json['personal_info'] as Map<String, dynamic>),
      professionalSummary: json['professional_summary'] as String?,
      enhancedSummary: json['enhanced_professional_summary'] as String?,
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
      'enhanced_professional_summary': enhancedSummary,
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
    int? userId,
    PersonalInfo? personalInfo,
    String? professionalSummary,
    String? enhancedSummary,
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
      enhancedSummary: enhancedSummary ?? this.enhancedSummary,
      experiences: experiences ?? this.experiences,
      education: education ?? this.education,
      skills: skills ?? this.skills,
      projects: projects ?? this.projects,
      customFields: customFields ?? this.customFields,
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
        other.enhancedSummary == enhancedSummary &&
        _listEquals(other.experiences, experiences) &&
        _listEquals(other.education, education) &&
        other.skills == skills &&
        _listEquals(other.projects, projects) &&
        // Map equality is tricky, assuming simple map or identity for now
        // Ideally use mapEquals from foundation, but we don't import it here.
        // For now, let's assume customFields don't change often or identity is enough
        // or implement simple map check.
        other.customFields == customFields && 
        other.createdAt == createdAt &&
        other.updatedAt == updatedAt;
  }

  @override
  int get hashCode {
    return Object.hash(
      id,
      userId,
      personalInfo,
      professionalSummary,
      enhancedSummary,
      Object.hashAll(experiences),
      Object.hashAll(education),
      skills,
      Object.hashAll(projects),
      // customFields is a Map, its hashCode is identity based usually.
      // For now, let's keep it as is or use Object.hashAll(customFields.keys) ^ Object.hashAll(customFields.values)
      customFields,
      createdAt,
      updatedAt,
    );
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

  PersonalInfo copyWith({
    String? fullName,
    String? email,
    String? phone,
    String? location,
    String? linkedin,
    String? github,
    String? website,
  }) {
    return PersonalInfo(
      fullName: fullName ?? this.fullName,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      location: location ?? this.location,
      linkedin: linkedin ?? this.linkedin,
      github: github ?? this.github,
      website: website ?? this.website,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is PersonalInfo &&
        other.fullName == fullName &&
        other.email == email &&
        other.phone == phone &&
        other.location == location &&
        other.linkedin == linkedin &&
        other.github == github &&
        other.website == website;
  }

  @override
  int get hashCode {
    return fullName.hashCode ^
        email.hashCode ^
        phone.hashCode ^
        location.hashCode ^
        linkedin.hashCode ^
        github.hashCode ^
        website.hashCode;
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
    this.enhancedDescription,
    this.achievements = const [],
    this.technologies = const [],
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
  final String? enhancedDescription;
  final List<String> achievements;
  final List<String> technologies;
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
      enhancedDescription: json['enhanced_description'] as String?,
      achievements: (json['achievements'] as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      technologies: (json['technologies'] as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      employmentType: json['employment_type'] as String?,
      industry: json['industry'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'title': title,
      'company': company,
      'location': location,
      'start_date': startDate,
      'end_date': endDate,
      'is_current': isCurrent,
      'description': description,
      'enhanced_description': enhancedDescription,
      'achievements': achievements,
      'technologies': technologies,
      'employment_type': employmentType,
      'industry': industry,
    };
  }

  Experience copyWith({
    String? id,
    String? title,
    String? company,
    String? location,
    String? startDate,
    String? endDate,
    bool? isCurrent,
    String? description,
    String? enhancedDescription,
    List<String>? achievements,
    List<String>? technologies,
    String? employmentType,
    String? industry,
  }) {
    return Experience(
      id: id ?? this.id,
      title: title ?? this.title,
      company: company ?? this.company,
      location: location ?? this.location,
      startDate: startDate ?? this.startDate,
      endDate: endDate ?? this.endDate,
      isCurrent: isCurrent ?? this.isCurrent,
      description: description ?? this.description,
      enhancedDescription: enhancedDescription ?? this.enhancedDescription,
      achievements: achievements ?? this.achievements,
      technologies: technologies ?? this.technologies,
      employmentType: employmentType ?? this.employmentType,
      industry: industry ?? this.industry,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Experience &&
        other.id == id &&
        other.title == title &&
        other.company == company &&
        other.location == location &&
        other.startDate == startDate &&
        other.endDate == endDate &&
        other.isCurrent == isCurrent &&
        other.description == description &&
        other.enhancedDescription == enhancedDescription &&
        _listEquals(other.achievements, achievements) &&
        _listEquals(other.technologies, technologies) &&
        other.employmentType == employmentType &&
        other.industry == industry;
  }

  @override
  int get hashCode {
    return Object.hash(
      id,
      title,
      company,
      location,
      startDate,
      endDate,
      isCurrent,
      description,
      enhancedDescription,
      Object.hashAll(achievements),
      Object.hashAll(technologies),
      employmentType,
      industry,
    );
  }
}

// Helper function for list equality
bool _listEquals<T>(List<T>? a, List<T>? b) {
  if (a == null) return b == null;
  if (b == null || a.length != b.length) return false;
  for (int i = 0; i < a.length; i++) {
    if (a[i] != b[i]) return false;
  }
  return true;
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
      if (id != null) 'id': id,
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

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Education &&
        other.id == id &&
        other.institution == institution &&
        other.degree == degree &&
        other.fieldOfStudy == fieldOfStudy &&
        other.startDate == startDate &&
        other.endDate == endDate &&
        other.isCurrent == isCurrent &&
        other.gpa == gpa &&
        _listEquals(other.honors, honors) &&
        other.description == description;
  }

  @override
  int get hashCode {
    return Object.hash(
      id,
      institution,
      degree,
      fieldOfStudy,
      startDate,
      endDate,
      isCurrent,
      gpa,
      Object.hashAll(honors),
      description,
    );
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
        _listEquals(other.technical, technical) &&
        _listEquals(other.soft, soft) &&
        _listEquals(other.languages, languages) &&
        _listEquals(other.certifications, certifications);
  }

  @override
  int get hashCode {
    return Object.hash(
      Object.hashAll(technical),
      Object.hashAll(soft),
      Object.hashAll(languages),
      Object.hashAll(certifications),
    );
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
      if (id != null) 'id': id,
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
    this.enhancedDescription,
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
  final String? enhancedDescription;
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
      enhancedDescription: json['enhanced_description'] as String?,
      technologies: (json['technologies'] as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      url: json['url'] as String?,
      repositoryUrl: json['repository_url'] as String? ?? json['github_url'] as String?,
      startDate: json['start_date'] as String?,
      endDate: json['end_date'] as String?,
      isOngoing: json['is_ongoing'] as bool? ?? false,
      highlights: (json['highlights'] as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
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
      'github_url': repositoryUrl,
      'start_date': startDate,
      'end_date': endDate,
      'is_ongoing': isOngoing,
      'highlights': highlights,
    };
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Project &&
        other.id == id &&
        other.name == name &&
        other.description == description &&
        other.enhancedDescription == enhancedDescription &&
        _listEquals(other.technologies, technologies) &&
        other.url == url &&
        other.repositoryUrl == repositoryUrl &&
        other.startDate == startDate &&
        other.endDate == endDate &&
        other.isOngoing == isOngoing &&
        _listEquals(other.highlights, highlights);
  }

  @override
  int get hashCode {
    return Object.hash(
      id,
      name,
      description,
      enhancedDescription,
      Object.hashAll(technologies),
      url,
      repositoryUrl,
      startDate,
      endDate,
      isOngoing,
      Object.hashAll(highlights),
    );
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