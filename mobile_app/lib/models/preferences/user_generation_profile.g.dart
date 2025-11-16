// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_generation_profile.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$UserGenerationProfileImpl _$$UserGenerationProfileImplFromJson(
  Map<String, dynamic> json,
) => _$UserGenerationProfileImpl(
  id: json['id'] as String,
  userId: (json['userId'] as num).toInt(),
  layoutConfigId: json['layoutConfigId'] as String?,
  writingStyleConfigId: json['writingStyleConfigId'] as String?,
  targetAtsScore: (json['targetAtsScore'] as num).toDouble(),
  maxBulletsPerRole: (json['maxBulletsPerRole'] as num).toInt(),
  createdAt: DateTime.parse(json['createdAt'] as String),
  updatedAt: DateTime.parse(json['updatedAt'] as String),
);

Map<String, dynamic> _$$UserGenerationProfileImplToJson(
  _$UserGenerationProfileImpl instance,
) => <String, dynamic>{
  'id': instance.id,
  'userId': instance.userId,
  'layoutConfigId': instance.layoutConfigId,
  'writingStyleConfigId': instance.writingStyleConfigId,
  'targetAtsScore': instance.targetAtsScore,
  'maxBulletsPerRole': instance.maxBulletsPerRole,
  'createdAt': instance.createdAt.toIso8601String(),
  'updatedAt': instance.updatedAt.toIso8601String(),
};
