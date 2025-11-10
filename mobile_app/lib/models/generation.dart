import 'package:flutter/material.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'generation.freezed.dart';
part 'generation.g.dart';

/// Main generation model tracking AI pipeline progress and results
@freezed
class Generation with _$Generation {
  const factory Generation({
    required String id,
    required String profileId,
    required String jobId,
    required DocumentType documentType,
    required GenerationStatus status,
    required GenerationProgress progress,
    GenerationResult? result,
    String? errorMessage,
    @Default(0) int tokensUsed,
    double? generationTime,
    required DateTime createdAt,
    DateTime? completedAt,
    DateTime? startedAt,
    DateTime? updatedAt,
    String? estimatedCompletion,
  }) = _Generation;

  factory Generation.fromJson(Map<String, dynamic> json) =>
      _$GenerationFromJson(json);
}

/// Pagination metadata for generation lists
@freezed
class Pagination with _$Pagination {
  const factory Pagination({
    required int total,
    required int limit,
    required int offset,
    required bool hasNext,
    required bool hasPrevious,
  }) = _Pagination;

  factory Pagination.fromJson(Map<String, dynamic> json) =>
      _$PaginationFromJson(json);
}

/// Generation status enum
enum GenerationStatus {
  @JsonValue('pending')
  pending,
  @JsonValue('generating')
  generating,
  @JsonValue('completed')
  completed,
  @JsonValue('failed')
  failed,
  @JsonValue('cancelled')
  cancelled,
}

/// Document type enum
enum DocumentType {
  @JsonValue('resume')
  resume,
  @JsonValue('cover_letter')
  coverLetter,
}

/// Generation progress tracking with stage information
@freezed
class GenerationProgress with _$GenerationProgress {
  const factory GenerationProgress({
    required int currentStage,
    required int totalStages,
    required int percentage,
    String? stageName,
    String? stageDescription,
  }) = _GenerationProgress;

  factory GenerationProgress.fromJson(Map<String, dynamic> json) =>
      _$GenerationProgressFromJson(json);

  /// Initial progress state (queued)
  factory GenerationProgress.initial() => const GenerationProgress(
        currentStage: 0,
        totalStages: 5,
        percentage: 0,
        stageName: null,
        stageDescription: 'Queued for processing',
      );
}

/// Generation result with ATS scores and recommendations
@freezed
class GenerationResult with _$GenerationResult {
  const factory GenerationResult({
    required String documentId,
    required double atsScore,
    required int matchPercentage,
    required double keywordCoverage,
    required int keywordsMatched,
    required int keywordsTotal,
    required String pdfUrl,
    @Default([]) List<String> recommendations,
  }) = _GenerationResult;

  factory GenerationResult.fromJson(Map<String, dynamic> json) =>
      _$GenerationResultFromJson(json);
}

/// Generation options for customizing output
@freezed
class GenerationOptions with _$GenerationOptions {
  const factory GenerationOptions({
    @Default('modern') String template,
    @Default('one_page') String length,
    @Default([]) List<String> focusAreas,
    @Default(false) bool includeCoverLetter,
    String? customInstructions,
  }) = _GenerationOptions;

  factory GenerationOptions.fromJson(Map<String, dynamic> json) =>
      _$GenerationOptionsFromJson(json);

  /// Convert to JSON for API requests
  static Map<String, dynamic> toRequestJson(GenerationOptions options) {
    return {
      'template': options.template,
      'length': options.length,
      'focus_areas': options.focusAreas,
      'include_cover_letter': options.includeCoverLetter,
      if (options.customInstructions != null &&
          options.customInstructions!.isNotEmpty)
        'custom_instructions': options.customInstructions,
    };
  }
}

/// Resume template information
@freezed
class Template with _$Template {
  const factory Template({
    required String id,
    required String name,
    required String description,
    required String previewUrl,
    required List<String> recommendedFor,
    required bool atsFriendly,
  }) = _Template;

  factory Template.fromJson(Map<String, dynamic> json) =>
      _$TemplateFromJson(json);
}

/// Generation list item for simplified list view
@freezed
class GenerationListItem with _$GenerationListItem {
  const factory GenerationListItem({
    required String id,
    required GenerationStatus status,
    required DocumentType documentType,
    required String jobTitle,
    required String company,
    double? atsScore,
    required DateTime createdAt,
    DateTime? completedAt,
  }) = _GenerationListItem;

  factory GenerationListItem.fromJson(Map<String, dynamic> json) =>
      _$GenerationListItemFromJson(json);
}

/// Statistics for generation overview
@freezed
class GenerationStatistics with _$GenerationStatistics {
  const factory GenerationStatistics({
    required int totalGenerations,
    required int completed,
    required int failed,
    required int inProgress,
    required double averageAtsScore,
  }) = _GenerationStatistics;

  factory GenerationStatistics.fromJson(Map<String, dynamic> json) =>
      _$GenerationStatisticsFromJson(json);
}

/// Extension methods for Generation
extension GenerationExtensions on Generation {
  /// Check if generation is complete
  bool get isComplete => status == GenerationStatus.completed;

  /// Check if generation failed
  bool get isFailed => status == GenerationStatus.failed;

  /// Check if generation is currently processing
  bool get isProcessing =>
      status == GenerationStatus.generating ||
      status == GenerationStatus.pending;

  /// Check if generation can be cancelled
  bool get canCancel => isProcessing;

  /// Get display text for status
  String get statusDisplayText {
    switch (status) {
      case GenerationStatus.pending:
        return 'Queued';
      case GenerationStatus.generating:
        return 'Generating...';
      case GenerationStatus.completed:
        return 'Completed';
      case GenerationStatus.failed:
        return 'Failed';
      case GenerationStatus.cancelled:
        return 'Cancelled';
    }
  }

  /// Get color for status
  Color get statusColor {
    switch (status) {
      case GenerationStatus.pending:
      case GenerationStatus.generating:
        return Colors.blue;
      case GenerationStatus.completed:
        return Colors.green;
      case GenerationStatus.failed:
      case GenerationStatus.cancelled:
        return Colors.red;
    }
  }
}
