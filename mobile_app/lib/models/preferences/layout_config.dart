// lib/models/preferences/layout_config.dart

import 'package:freezed_annotation/freezed_annotation.dart';

part 'layout_config.freezed.dart';
part 'layout_config.g.dart';

@freezed
class LayoutConfig with _$LayoutConfig {
  const LayoutConfig._();
  
  const factory LayoutConfig({
    required String id,
    required int userId,
    required List<String> sectionOrder,
    required String bulletStyle,
    required String contentDensity,
    required String contactInfoFormat,
    required Map<String, dynamic> extractionMetadata,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _LayoutConfig;

  factory LayoutConfig.fromJson(Map<String, dynamic> json) =>
      _$LayoutConfigFromJson(json);


  String get bulletStyleDisplay {
    switch (bulletStyle) {
      case 'action_verb':
        return 'Action Verb Focus';
      case 'results_focused':
        return 'Results-Focused';
      case 'hybrid':
        return 'Hybrid Style';
      default:
        return bulletStyle;
    }
  }

  String get densityDisplay {
    switch (contentDensity) {
      case 'concise':
        return 'Concise (2-3 bullets)';
      case 'balanced':
        return 'Balanced (4-5 bullets)';
      case 'detailed':
        return 'Detailed (6+ bullets)';
      default:
        return contentDensity;
    }
  }

  String get contactInfoDisplay {
    switch (contactInfoFormat) {
      case 'header_left':
        return 'Header - Left Aligned';
      case 'header_center':
        return 'Header - Center Aligned';
      case 'header_right':
        return 'Header - Right Aligned';
      default:
        return contactInfoFormat;
    }
  }

  double get confidenceScore {
    final metadata = extractionMetadata;
    if (metadata.containsKey('confidence_score')) {
      final score = metadata['confidence_score'];
      if (score is num) {
        return score.toDouble();
      }
    }
    return 0.0;
  }
}
