class Template {
  final String id;
  final String name;
  final String description;
  final int atsScore;
  final List<String> industries;
  final TemplateCustomization supportsCustomization;
  final String? previewUrl;

  Template({
    required this.id,
    required this.name,
    required this.description,
    required this.atsScore,
    required this.industries,
    required this.supportsCustomization,
    this.previewUrl,
  });

  factory Template.fromJson(Map<String, dynamic> json) {
    return Template(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      atsScore: json['ats_score'] ?? 0,
      industries: List<String>.from(json['industries'] ?? []),
      supportsCustomization: TemplateCustomization.fromJson(
        json['supports_customization'] ?? {}
      ),
      previewUrl: json['preview_url'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'ats_score': atsScore,
      'industries': industries,
      'supports_customization': supportsCustomization.toJson(),
      'preview_url': previewUrl,
    };
  }

  String get atsScoreDisplay => '$atsScore% ATS Score';

  bool get isHighAtsScore => atsScore >= 90;
}

class TemplateCustomization {
  final bool accentColor;
  final bool fontFamily;

  TemplateCustomization({
    required this.accentColor,
    required this.fontFamily,
  });

  factory TemplateCustomization.fromJson(Map<String, dynamic> json) {
    return TemplateCustomization(
      accentColor: json['accent_color'] ?? false,
      fontFamily: json['font_family'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'accent_color': accentColor,
      'font_family': fontFamily,
    };
  }
}

class ExportOptions {
  final String templateId;
  final String format; // 'pdf' or 'docx'
  final String? fontFamily;
  final String? accentColor;
  final String lineSpacing; // 'tight', 'normal', 'relaxed'
  final String margins; // 'narrow', 'normal', 'wide'
  final String? customFilename;
  final bool includeMetadata;

  ExportOptions({
    required this.templateId,
    this.format = 'pdf',
    this.fontFamily,
    this.accentColor,
    this.lineSpacing = 'normal',
    this.margins = 'normal',
    this.customFilename,
    this.includeMetadata = false,
  });

  Map<String, dynamic> toJson() {
    return {
      'template': templateId,
      'format': format,
      if (fontFamily != null) 'font_family': fontFamily,
      if (accentColor != null) 'accent_color': accentColor,
      'line_spacing': lineSpacing,
      'margins': margins,
      if (customFilename != null) 'custom_filename': customFilename,
      'include_metadata': includeMetadata,
    };
  }

  ExportOptions copyWith({
    String? templateId,
    String? format,
    String? fontFamily,
    String? accentColor,
    String? lineSpacing,
    String? margins,
    String? customFilename,
    bool? includeMetadata,
  }) {
    return ExportOptions(
      templateId: templateId ?? this.templateId,
      format: format ?? this.format,
      fontFamily: fontFamily ?? this.fontFamily,
      accentColor: accentColor ?? this.accentColor,
      lineSpacing: lineSpacing ?? this.lineSpacing,
      margins: margins ?? this.margins,
      customFilename: customFilename ?? this.customFilename,
      includeMetadata: includeMetadata ?? this.includeMetadata,
    );
  }
}
