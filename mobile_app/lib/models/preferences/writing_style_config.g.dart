// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'writing_style_config.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$WritingStyleConfigImpl _$$WritingStyleConfigImplFromJson(
  Map<String, dynamic> json,
) => _$WritingStyleConfigImpl(
  id: json['id'] as String,
  userId: (json['userId'] as num).toInt(),
  tone: json['tone'] as String,
  toneLevel: (json['toneLevel'] as num).toInt(),
  formalityLevel: (json['formalityLevel'] as num).toInt(),
  sentenceComplexity: json['sentenceComplexity'] as String,
  vocabularyLevel: json['vocabularyLevel'] as String,
  avgParagraphLength: (json['avgParagraphLength'] as num).toInt(),
  sourceText: json['sourceText'] as String,
  extractionMetadata: json['extractionMetadata'] as Map<String, dynamic>,
  createdAt: DateTime.parse(json['createdAt'] as String),
  updatedAt: DateTime.parse(json['updatedAt'] as String),
);

Map<String, dynamic> _$$WritingStyleConfigImplToJson(
  _$WritingStyleConfigImpl instance,
) => <String, dynamic>{
  'id': instance.id,
  'userId': instance.userId,
  'tone': instance.tone,
  'toneLevel': instance.toneLevel,
  'formalityLevel': instance.formalityLevel,
  'sentenceComplexity': instance.sentenceComplexity,
  'vocabularyLevel': instance.vocabularyLevel,
  'avgParagraphLength': instance.avgParagraphLength,
  'sourceText': instance.sourceText,
  'extractionMetadata': instance.extractionMetadata,
  'createdAt': instance.createdAt.toIso8601String(),
  'updatedAt': instance.updatedAt.toIso8601String(),
};
