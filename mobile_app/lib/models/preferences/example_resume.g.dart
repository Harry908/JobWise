// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'example_resume.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ExampleResumeImpl _$$ExampleResumeImplFromJson(Map<String, dynamic> json) =>
    _$ExampleResumeImpl(
      id: json['id'] as String,
      userId: (json['userId'] as num).toInt(),
      filePath: json['filePath'] as String,
      originalFilename: json['originalFilename'] as String,
      layoutConfigId: json['layoutConfigId'] as String,
      isPrimary: json['isPrimary'] as bool,
      fileHash: json['fileHash'] as String?,
      uploadedAt: DateTime.parse(json['uploadedAt'] as String),
      fileSize: (json['fileSize'] as num).toInt(),
      fileType: json['fileType'] as String,
    );

Map<String, dynamic> _$$ExampleResumeImplToJson(_$ExampleResumeImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'userId': instance.userId,
      'filePath': instance.filePath,
      'originalFilename': instance.originalFilename,
      'layoutConfigId': instance.layoutConfigId,
      'isPrimary': instance.isPrimary,
      'fileHash': instance.fileHash,
      'uploadedAt': instance.uploadedAt.toIso8601String(),
      'fileSize': instance.fileSize,
      'fileType': instance.fileType,
    };
