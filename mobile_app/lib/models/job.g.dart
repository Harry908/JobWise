// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'job.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$JobImpl _$$JobImplFromJson(Map<String, dynamic> json) => _$JobImpl(
  id: json['id'] as String,
  userId: json['userId'] as String?,
  source: $enumDecode(_$JobSourceEnumMap, json['source']),
  title: json['title'] as String,
  company: json['company'] as String,
  location: json['location'] as String?,
  description: json['description'] as String?,
  rawText: json['rawText'] as String?,
  parsedKeywords:
      (json['parsedKeywords'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList() ??
      const [],
  requirements:
      (json['requirements'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList() ??
      const [],
  benefits:
      (json['benefits'] as List<dynamic>?)?.map((e) => e as String).toList() ??
      const [],
  salaryRange: json['salaryRange'] as String?,
  remote: json['remote'] as bool? ?? false,
  status:
      $enumDecodeNullable(_$JobStatusEnumMap, json['status']) ??
      JobStatus.active,
  applicationStatus:
      $enumDecodeNullable(
        _$ApplicationStatusEnumMap,
        json['applicationStatus'],
      ) ??
      ApplicationStatus.notApplied,
  createdAt: DateTime.parse(json['createdAt'] as String),
  updatedAt: DateTime.parse(json['updatedAt'] as String),
);

Map<String, dynamic> _$$JobImplToJson(_$JobImpl instance) => <String, dynamic>{
  'id': instance.id,
  'userId': instance.userId,
  'source': _$JobSourceEnumMap[instance.source]!,
  'title': instance.title,
  'company': instance.company,
  'location': instance.location,
  'description': instance.description,
  'rawText': instance.rawText,
  'parsedKeywords': instance.parsedKeywords,
  'requirements': instance.requirements,
  'benefits': instance.benefits,
  'salaryRange': instance.salaryRange,
  'remote': instance.remote,
  'status': _$JobStatusEnumMap[instance.status]!,
  'applicationStatus': _$ApplicationStatusEnumMap[instance.applicationStatus]!,
  'createdAt': instance.createdAt.toIso8601String(),
  'updatedAt': instance.updatedAt.toIso8601String(),
};

const _$JobSourceEnumMap = {
  JobSource.userCreated: 'user_created',
  JobSource.indeed: 'indeed',
  JobSource.linkedin: 'linkedin',
  JobSource.glassdoor: 'glassdoor',
  JobSource.mock: 'mock',
  JobSource.imported: 'imported',
  JobSource.urlImport: 'url_import',
};

const _$JobStatusEnumMap = {
  JobStatus.active: 'active',
  JobStatus.archived: 'archived',
  JobStatus.draft: 'draft',
};

const _$ApplicationStatusEnumMap = {
  ApplicationStatus.notApplied: 'not_applied',
  ApplicationStatus.preparing: 'preparing',
  ApplicationStatus.applied: 'applied',
  ApplicationStatus.interviewing: 'interviewing',
  ApplicationStatus.offerReceived: 'offer_received',
  ApplicationStatus.rejected: 'rejected',
  ApplicationStatus.accepted: 'accepted',
  ApplicationStatus.withdrawn: 'withdrawn',
};

_$BrowseJobImpl _$$BrowseJobImplFromJson(Map<String, dynamic> json) =>
    _$BrowseJobImpl(
      id: json['id'] as String,
      source: $enumDecode(_$JobSourceEnumMap, json['source']),
      title: json['title'] as String,
      company: json['company'] as String,
      location: json['location'] as String?,
      description: json['description'] as String?,
      parsedKeywords:
          (json['parsedKeywords'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      requirements:
          (json['requirements'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      benefits:
          (json['benefits'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      salaryRange: json['salaryRange'] as String?,
      remote: json['remote'] as bool? ?? false,
    );

Map<String, dynamic> _$$BrowseJobImplToJson(_$BrowseJobImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'source': _$JobSourceEnumMap[instance.source]!,
      'title': instance.title,
      'company': instance.company,
      'location': instance.location,
      'description': instance.description,
      'parsedKeywords': instance.parsedKeywords,
      'requirements': instance.requirements,
      'benefits': instance.benefits,
      'salaryRange': instance.salaryRange,
      'remote': instance.remote,
    };

_$JobListResponseImpl _$$JobListResponseImplFromJson(
  Map<String, dynamic> json,
) => _$JobListResponseImpl(
  jobs: (json['jobs'] as List<dynamic>)
      .map((e) => Job.fromJson(e as Map<String, dynamic>))
      .toList(),
  total: (json['total'] as num).toInt(),
  pagination: PaginationMeta.fromJson(
    json['pagination'] as Map<String, dynamic>,
  ),
);

Map<String, dynamic> _$$JobListResponseImplToJson(
  _$JobListResponseImpl instance,
) => <String, dynamic>{
  'jobs': instance.jobs,
  'total': instance.total,
  'pagination': instance.pagination,
};

_$BrowseJobListResponseImpl _$$BrowseJobListResponseImplFromJson(
  Map<String, dynamic> json,
) => _$BrowseJobListResponseImpl(
  jobs: (json['jobs'] as List<dynamic>)
      .map((e) => BrowseJob.fromJson(e as Map<String, dynamic>))
      .toList(),
  total: (json['total'] as num).toInt(),
  pagination: PaginationMeta.fromJson(
    json['pagination'] as Map<String, dynamic>,
  ),
);

Map<String, dynamic> _$$BrowseJobListResponseImplToJson(
  _$BrowseJobListResponseImpl instance,
) => <String, dynamic>{
  'jobs': instance.jobs,
  'total': instance.total,
  'pagination': instance.pagination,
};

_$PaginationMetaImpl _$$PaginationMetaImplFromJson(Map<String, dynamic> json) =>
    _$PaginationMetaImpl(
      limit: (json['limit'] as num).toInt(),
      offset: (json['offset'] as num).toInt(),
      total: (json['total'] as num).toInt(),
      hasMore: json['hasMore'] as bool,
    );

Map<String, dynamic> _$$PaginationMetaImplToJson(
  _$PaginationMetaImpl instance,
) => <String, dynamic>{
  'limit': instance.limit,
  'offset': instance.offset,
  'total': instance.total,
  'hasMore': instance.hasMore,
};

_$CreateJobFromTextRequestImpl _$$CreateJobFromTextRequestImplFromJson(
  Map<String, dynamic> json,
) => _$CreateJobFromTextRequestImpl(
  source:
      $enumDecodeNullable(_$JobSourceEnumMap, json['source']) ??
      JobSource.userCreated,
  rawText: json['rawText'] as String,
);

Map<String, dynamic> _$$CreateJobFromTextRequestImplToJson(
  _$CreateJobFromTextRequestImpl instance,
) => <String, dynamic>{
  'source': _$JobSourceEnumMap[instance.source]!,
  'rawText': instance.rawText,
};

_$CreateJobFromUrlRequestImpl _$$CreateJobFromUrlRequestImplFromJson(
  Map<String, dynamic> json,
) => _$CreateJobFromUrlRequestImpl(
  source:
      $enumDecodeNullable(_$JobSourceEnumMap, json['source']) ??
      JobSource.urlImport,
  url: json['url'] as String,
);

Map<String, dynamic> _$$CreateJobFromUrlRequestImplToJson(
  _$CreateJobFromUrlRequestImpl instance,
) => <String, dynamic>{
  'source': _$JobSourceEnumMap[instance.source]!,
  'url': instance.url,
};

_$UpdateJobRequestImpl _$$UpdateJobRequestImplFromJson(
  Map<String, dynamic> json,
) => _$UpdateJobRequestImpl(
  parsedKeywords: (json['parsedKeywords'] as List<dynamic>?)
      ?.map((e) => e as String)
      .toList(),
  status: $enumDecodeNullable(_$JobStatusEnumMap, json['status']),
  applicationStatus: $enumDecodeNullable(
    _$ApplicationStatusEnumMap,
    json['applicationStatus'],
  ),
);

Map<String, dynamic> _$$UpdateJobRequestImplToJson(
  _$UpdateJobRequestImpl instance,
) => <String, dynamic>{
  'parsedKeywords': instance.parsedKeywords,
  'status': _$JobStatusEnumMap[instance.status],
  'applicationStatus': _$ApplicationStatusEnumMap[instance.applicationStatus],
};
