import 'package:freezed_annotation/freezed_annotation.dart';

part 'sample.freezed.dart';
part 'sample.g.dart';

/// Sample document model (resume or cover letter sample)
@freezed
class Sample with _$Sample {
  const factory Sample({
    required String id,
    @JsonKey(name: 'user_id') required int userId,
    @JsonKey(name: 'document_type') required String documentType, // 'resume' or 'cover_letter'
    @JsonKey(name: 'original_filename') required String originalFilename,
    @JsonKey(name: 'content_text') String? contentText, // Full text content
    @JsonKey(name: 'word_count') required int wordCount,
    @JsonKey(name: 'character_count') required int characterCount,
    @JsonKey(name: 'is_active') @Default(true) bool isActive,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    @JsonKey(name: 'updated_at') DateTime? updatedAt,
  }) = _Sample;

  factory Sample.fromJson(Map<String, dynamic> json) => _$SampleFromJson(json);
}

/// Sample list response model
@freezed
class SampleListResponse with _$SampleListResponse {
  const factory SampleListResponse({
    required List<Sample> items,
    required int total,
  }) = _SampleListResponse;

  factory SampleListResponse.fromJson(Map<String, dynamic> json) =>
      _$SampleListResponseFromJson(json);
}
