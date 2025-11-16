// lib/models/preferences/example_resume.dart

import 'package:freezed_annotation/freezed_annotation.dart';

part 'example_resume.freezed.dart';
part 'example_resume.g.dart';

@freezed
class ExampleResume with _$ExampleResume {
  const ExampleResume._();
  
  const factory ExampleResume({
    required String id,
    required int userId,
    required String filePath,
    required String originalFilename,
    required String layoutConfigId,
    required bool isPrimary,
    String? fileHash,
    required DateTime uploadedAt,
    required int fileSize,
    required String fileType,
  }) = _ExampleResume;

  factory ExampleResume.fromJson(Map<String, dynamic> json) =>
      _$ExampleResumeFromJson(json);
      
  String get fileSizeFormatted {
    final kb = fileSize / 1024;
    if (kb < 1024) {
      return '${kb.toStringAsFixed(1)} KB';
    }
    final mb = kb / 1024;
    return '${mb.toStringAsFixed(1)} MB';
  }

  String get fileTypeDisplay {
    switch (fileType.toLowerCase()) {
      case 'pdf':
        return 'PDF';
      case 'docx':
        return 'Word Document';
      case 'txt':
        return 'Text File';
      default:
        return fileType.toUpperCase();
    }
  }
}


