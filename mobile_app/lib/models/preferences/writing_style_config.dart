// lib/models/preferences/writing_style_config.dart

import 'package:freezed_annotation/freezed_annotation.dart';

part 'writing_style_config.freezed.dart';
part 'writing_style_config.g.dart';

@freezed
class WritingStyleConfig with _$WritingStyleConfig {
  const WritingStyleConfig._();
  
  const factory WritingStyleConfig({
    required String id,
    required int userId,
    required String tone,
    required int toneLevel,
    required int formalityLevel,
    required String sentenceComplexity,
    required String vocabularyLevel,
    required int avgParagraphLength,
    required String sourceText,
    required Map<String, dynamic> extractionMetadata,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _WritingStyleConfig;

  factory WritingStyleConfig.fromJson(Map<String, dynamic> json) =>
      _$WritingStyleConfigFromJson(json);


  String get toneDisplay {
    switch (tone) {
      case 'professional':
        return 'Professional';
      case 'professional_enthusiastic':
        return 'Professional & Enthusiastic';
      case 'authoritative':
        return 'Authoritative';
      case 'conversational':
        return 'Conversational';
      default:
        return tone;
    }
  }

  String get formalityDisplay {
    if (formalityLevel >= 8) return 'Very Formal';
    if (formalityLevel >= 6) return 'Business Professional';
    if (formalityLevel >= 4) return 'Moderate';
    return 'Casual';
  }

  String get complexityDisplay {
    switch (sentenceComplexity) {
      case 'simple':
        return 'Simple & Direct';
      case 'varied':
        return 'Varied Mix';
      case 'complex':
        return 'Complex & Detailed';
      default:
        return sentenceComplexity;
    }
  }

  String get vocabularyDisplay {
    switch (vocabularyLevel) {
      case 'basic':
        return 'Basic';
      case 'professional':
        return 'Professional';
      case 'advanced_professional':
        return 'Advanced Professional';
      default:
        return vocabularyLevel;
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
