// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'generation.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$GenerationImpl _$$GenerationImplFromJson(Map<String, dynamic> json) =>
    _$GenerationImpl(
      id: json['id'] as String,
      profileId: json['profileId'] as String,
      jobId: json['jobId'] as String,
      documentType: $enumDecode(_$DocumentTypeEnumMap, json['documentType']),
      status: $enumDecode(_$GenerationStatusEnumMap, json['status']),
      progress: GenerationProgress.fromJson(
        json['progress'] as Map<String, dynamic>,
      ),
      result: json['result'] == null
          ? null
          : GenerationResult.fromJson(json['result'] as Map<String, dynamic>),
      errorMessage: json['errorMessage'] as String?,
      tokensUsed: (json['tokensUsed'] as num?)?.toInt() ?? 0,
      generationTime: (json['generationTime'] as num?)?.toDouble(),
      createdAt: DateTime.parse(json['createdAt'] as String),
      completedAt: json['completedAt'] == null
          ? null
          : DateTime.parse(json['completedAt'] as String),
      startedAt: json['startedAt'] == null
          ? null
          : DateTime.parse(json['startedAt'] as String),
      updatedAt: json['updatedAt'] == null
          ? null
          : DateTime.parse(json['updatedAt'] as String),
      estimatedCompletion: json['estimatedCompletion'] as String?,
    );

Map<String, dynamic> _$$GenerationImplToJson(_$GenerationImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'profileId': instance.profileId,
      'jobId': instance.jobId,
      'documentType': _$DocumentTypeEnumMap[instance.documentType]!,
      'status': _$GenerationStatusEnumMap[instance.status]!,
      'progress': instance.progress,
      'result': instance.result,
      'errorMessage': instance.errorMessage,
      'tokensUsed': instance.tokensUsed,
      'generationTime': instance.generationTime,
      'createdAt': instance.createdAt.toIso8601String(),
      'completedAt': instance.completedAt?.toIso8601String(),
      'startedAt': instance.startedAt?.toIso8601String(),
      'updatedAt': instance.updatedAt?.toIso8601String(),
      'estimatedCompletion': instance.estimatedCompletion,
    };

const _$DocumentTypeEnumMap = {
  DocumentType.resume: 'resume',
  DocumentType.coverLetter: 'cover_letter',
};

const _$GenerationStatusEnumMap = {
  GenerationStatus.pending: 'pending',
  GenerationStatus.generating: 'generating',
  GenerationStatus.completed: 'completed',
  GenerationStatus.failed: 'failed',
  GenerationStatus.cancelled: 'cancelled',
};

_$PaginationImpl _$$PaginationImplFromJson(Map<String, dynamic> json) =>
    _$PaginationImpl(
      total: (json['total'] as num).toInt(),
      limit: (json['limit'] as num).toInt(),
      offset: (json['offset'] as num).toInt(),
      hasNext: json['hasNext'] as bool,
      hasPrevious: json['hasPrevious'] as bool,
    );

Map<String, dynamic> _$$PaginationImplToJson(_$PaginationImpl instance) =>
    <String, dynamic>{
      'total': instance.total,
      'limit': instance.limit,
      'offset': instance.offset,
      'hasNext': instance.hasNext,
      'hasPrevious': instance.hasPrevious,
    };

_$GenerationProgressImpl _$$GenerationProgressImplFromJson(
  Map<String, dynamic> json,
) => _$GenerationProgressImpl(
  currentStage: (json['currentStage'] as num).toInt(),
  totalStages: (json['totalStages'] as num).toInt(),
  percentage: (json['percentage'] as num).toInt(),
  stageName: json['stageName'] as String?,
  stageDescription: json['stageDescription'] as String?,
);

Map<String, dynamic> _$$GenerationProgressImplToJson(
  _$GenerationProgressImpl instance,
) => <String, dynamic>{
  'currentStage': instance.currentStage,
  'totalStages': instance.totalStages,
  'percentage': instance.percentage,
  'stageName': instance.stageName,
  'stageDescription': instance.stageDescription,
};

_$GenerationResultImpl _$$GenerationResultImplFromJson(
  Map<String, dynamic> json,
) => _$GenerationResultImpl(
  documentId: json['documentId'] as String,
  atsScore: (json['atsScore'] as num).toDouble(),
  matchPercentage: (json['matchPercentage'] as num).toInt(),
  keywordCoverage: (json['keywordCoverage'] as num).toDouble(),
  keywordsMatched: (json['keywordsMatched'] as num).toInt(),
  keywordsTotal: (json['keywordsTotal'] as num).toInt(),
  pdfUrl: json['pdfUrl'] as String,
  recommendations:
      (json['recommendations'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList() ??
      const [],
);

Map<String, dynamic> _$$GenerationResultImplToJson(
  _$GenerationResultImpl instance,
) => <String, dynamic>{
  'documentId': instance.documentId,
  'atsScore': instance.atsScore,
  'matchPercentage': instance.matchPercentage,
  'keywordCoverage': instance.keywordCoverage,
  'keywordsMatched': instance.keywordsMatched,
  'keywordsTotal': instance.keywordsTotal,
  'pdfUrl': instance.pdfUrl,
  'recommendations': instance.recommendations,
};

_$GenerationOptionsImpl _$$GenerationOptionsImplFromJson(
  Map<String, dynamic> json,
) => _$GenerationOptionsImpl(
  template: json['template'] as String? ?? 'modern',
  length: json['length'] as String? ?? 'one_page',
  focusAreas:
      (json['focusAreas'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList() ??
      const [],
  includeCoverLetter: json['includeCoverLetter'] as bool? ?? false,
  customInstructions: json['customInstructions'] as String?,
);

Map<String, dynamic> _$$GenerationOptionsImplToJson(
  _$GenerationOptionsImpl instance,
) => <String, dynamic>{
  'template': instance.template,
  'length': instance.length,
  'focusAreas': instance.focusAreas,
  'includeCoverLetter': instance.includeCoverLetter,
  'customInstructions': instance.customInstructions,
};

_$TemplateImpl _$$TemplateImplFromJson(Map<String, dynamic> json) =>
    _$TemplateImpl(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      previewUrl: json['previewUrl'] as String,
      recommendedFor: (json['recommendedFor'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      atsFriendly: json['atsFriendly'] as bool,
    );

Map<String, dynamic> _$$TemplateImplToJson(_$TemplateImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'previewUrl': instance.previewUrl,
      'recommendedFor': instance.recommendedFor,
      'atsFriendly': instance.atsFriendly,
    };

_$GenerationListItemImpl _$$GenerationListItemImplFromJson(
  Map<String, dynamic> json,
) => _$GenerationListItemImpl(
  id: json['id'] as String,
  status: $enumDecode(_$GenerationStatusEnumMap, json['status']),
  documentType: $enumDecode(_$DocumentTypeEnumMap, json['documentType']),
  jobTitle: json['jobTitle'] as String,
  company: json['company'] as String,
  atsScore: (json['atsScore'] as num?)?.toDouble(),
  createdAt: DateTime.parse(json['createdAt'] as String),
  completedAt: json['completedAt'] == null
      ? null
      : DateTime.parse(json['completedAt'] as String),
);

Map<String, dynamic> _$$GenerationListItemImplToJson(
  _$GenerationListItemImpl instance,
) => <String, dynamic>{
  'id': instance.id,
  'status': _$GenerationStatusEnumMap[instance.status]!,
  'documentType': _$DocumentTypeEnumMap[instance.documentType]!,
  'jobTitle': instance.jobTitle,
  'company': instance.company,
  'atsScore': instance.atsScore,
  'createdAt': instance.createdAt.toIso8601String(),
  'completedAt': instance.completedAt?.toIso8601String(),
};

_$GenerationStatisticsImpl _$$GenerationStatisticsImplFromJson(
  Map<String, dynamic> json,
) => _$GenerationStatisticsImpl(
  totalGenerations: (json['totalGenerations'] as num).toInt(),
  completed: (json['completed'] as num).toInt(),
  failed: (json['failed'] as num).toInt(),
  inProgress: (json['inProgress'] as num).toInt(),
  averageAtsScore: (json['averageAtsScore'] as num).toDouble(),
);

Map<String, dynamic> _$$GenerationStatisticsImplToJson(
  _$GenerationStatisticsImpl instance,
) => <String, dynamic>{
  'totalGenerations': instance.totalGenerations,
  'completed': instance.completed,
  'failed': instance.failed,
  'inProgress': instance.inProgress,
  'averageAtsScore': instance.averageAtsScore,
};
