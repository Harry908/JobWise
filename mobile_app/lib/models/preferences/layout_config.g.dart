// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'layout_config.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$LayoutConfigImpl _$$LayoutConfigImplFromJson(Map<String, dynamic> json) =>
    _$LayoutConfigImpl(
      id: json['id'] as String,
      userId: (json['userId'] as num).toInt(),
      sectionOrder: (json['sectionOrder'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      bulletStyle: json['bulletStyle'] as String,
      contentDensity: json['contentDensity'] as String,
      contactInfoFormat: json['contactInfoFormat'] as String,
      extractionMetadata: json['extractionMetadata'] as Map<String, dynamic>,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$$LayoutConfigImplToJson(_$LayoutConfigImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'userId': instance.userId,
      'sectionOrder': instance.sectionOrder,
      'bulletStyle': instance.bulletStyle,
      'contentDensity': instance.contentDensity,
      'contactInfoFormat': instance.contactInfoFormat,
      'extractionMetadata': instance.extractionMetadata,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
    };
