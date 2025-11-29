// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'sample.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$SampleImpl _$$SampleImplFromJson(Map<String, dynamic> json) => _$SampleImpl(
  id: json['id'] as String,
  userId: (json['user_id'] as num).toInt(),
  documentType: json['document_type'] as String,
  originalFilename: json['original_filename'] as String,
  contentText: json['content_text'] as String?,
  wordCount: (json['word_count'] as num).toInt(),
  characterCount: (json['character_count'] as num).toInt(),
  isActive: json['is_active'] as bool? ?? true,
  createdAt: DateTime.parse(json['created_at'] as String),
  updatedAt: json['updated_at'] == null
      ? null
      : DateTime.parse(json['updated_at'] as String),
);

Map<String, dynamic> _$$SampleImplToJson(_$SampleImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'document_type': instance.documentType,
      'original_filename': instance.originalFilename,
      'content_text': instance.contentText,
      'word_count': instance.wordCount,
      'character_count': instance.characterCount,
      'is_active': instance.isActive,
      'created_at': instance.createdAt.toIso8601String(),
      'updated_at': instance.updatedAt?.toIso8601String(),
    };

_$SampleListResponseImpl _$$SampleListResponseImplFromJson(
  Map<String, dynamic> json,
) => _$SampleListResponseImpl(
  items: (json['items'] as List<dynamic>)
      .map((e) => Sample.fromJson(e as Map<String, dynamic>))
      .toList(),
  total: (json['total'] as num).toInt(),
);

Map<String, dynamic> _$$SampleListResponseImplToJson(
  _$SampleListResponseImpl instance,
) => <String, dynamic>{'items': instance.items, 'total': instance.total};
